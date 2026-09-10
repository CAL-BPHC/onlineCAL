from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings

from ..admin.announcement import queue_announcement_emails
from ..factories import FacultyFactory, StudentFactory
from ..mail import MAX_RECIPIENTS_PER_EMAIL, UNDISCLOSED_RECIPIENTS
from ..models import Announcement, CustomUser
from ..models.email import EmailModel

LOCMEM_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@override_settings(EMAIL_BACKEND=LOCMEM_BACKEND)
class AnnouncementEmailTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 2 full batches and a partial one
        cls.user_count = 2 * MAX_RECIPIENTS_PER_EMAIL + 5
        cls.faculty = FacultyFactory(email="faculty@hyderabad.bits-pilani.ac.in")
        for i in range(cls.user_count - 1):
            StudentFactory(
                email=f"student{i}@hyderabad.bits-pilani.ac.in",
                supervisor=cls.faculty,
            )
        cls.inactive = StudentFactory(
            email="inactive@hyderabad.bits-pilani.ac.in",
            supervisor=cls.faculty,
            is_active=False,
        )
        cls.test_user = StudentFactory(email="tester@email.com", supervisor=cls.faculty)
        cls.expected_recipients = set(
            CustomUser.objects.filter(is_active=True)
            .exclude(email__endswith="@email.com")
            .values_list("email", flat=True)
        )

    def _announcement_emails(self):
        return EmailModel.objects.filter(
            email_type=EmailModel.NEW_ANNOUNCEMENT
        ).order_by("pk")

    def test_queues_one_email_per_batch_of_recipients(self):
        announcement = Announcement.objects.create(title="Maintenance", text="...")

        queued = queue_announcement_emails(announcement)

        emails = list(self._announcement_emails())
        self.assertEqual(queued, 3)
        self.assertEqual(len(emails), 3)
        self.assertEqual(
            [email.recipient_count for email in emails],
            [MAX_RECIPIENTS_PER_EMAIL, MAX_RECIPIENTS_PER_EMAIL, 5],
        )
        recipients = [address for email in emails for address in email.bcc_list]
        self.assertEqual(len(recipients), len(set(recipients)))
        self.assertEqual(set(recipients), self.expected_recipients)
        self.assertNotIn(self.inactive.email, recipients)
        self.assertNotIn(self.test_user.email, recipients)
        for email in emails:
            self.assertIsNone(email.receiver)
            self.assertFalse(email.sent)
            self.assertEqual(email.subject, "New CIF Announcement: Maintenance")
            self.assertIn("/announcements", email.text)
            self.assertIn("/announcements", email.text_html)
            # The announcement is the whole body: no generic greeting or
            # sign-off around it, only the do-not-reply footer
            for body in (email.text, email.text_html):
                self.assertNotIn("Dear User", body)
                self.assertNotIn("Portal Link", body)
                self.assertNotIn("Regards,", body)
                self.assertIn("system generated mail", body)

    def test_email_contains_the_announcement_text(self):
        announcement = Announcement.objects.create(
            title="R&D lab closed",
            text="The lab is closed on Friday.\nSee https://example.com/notice & plan ahead.",
        )

        queue_announcement_emails(announcement)

        email = self._announcement_emails().first()
        self.assertEqual(email.subject, "New CIF Announcement: R&D lab closed")
        # Plain text is sent as-is, without HTML escaping
        self.assertIn(
            "The lab is closed on Friday.\nSee https://example.com/notice & plan ahead.",
            email.text,
        )
        self.assertNotIn("&amp;", email.text)
        # HTML is escaped, line breaks become <br> and links are clickable
        self.assertIn("The lab is closed on Friday.<br>", email.text_html)
        self.assertIn('<a href="https://example.com/notice"', email.text_html)
        self.assertIn("&amp; plan ahead.", email.text_html)

    def test_html_in_announcement_text_is_escaped_in_the_html_email(self):
        announcement = Announcement.objects.create(
            title="<b>Bold</b>", text="<script>alert(1)</script>"
        )

        queue_announcement_emails(announcement)

        email = self._announcement_emails().first()
        self.assertNotIn("<script>", email.text_html)
        self.assertIn("&lt;script&gt;", email.text_html)

    def test_long_title_fits_in_the_subject(self):
        title = "x" * 100  # Announcement.title max_length
        announcement = Announcement.objects.create(title=title, text="...")

        queue_announcement_emails(announcement)

        email = self._announcement_emails().first()
        email.full_clean(exclude=["receiver"])
        self.assertEqual(email.subject, f"New CIF Announcement: {title}")

    def test_adding_an_announcement_in_admin_queues_batched_emails(self):
        admin_user = CustomUser.objects.create_superuser(
            email="admin@hyderabad.bits-pilani.ac.in",
            password="pass",
            name="Admin",
        )
        client = Client()
        client.force_login(admin_user)

        response = client.post(
            "/admin/booking_portal/announcement/add/",
            {"title": "New instrument", "text": "FESEM is back online."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 1)
        emails = self._announcement_emails()
        self.assertEqual(emails.count(), 3)
        # The superuser is an active user too
        self.assertEqual(
            sum(email.recipient_count for email in emails), self.user_count + 1
        )

    def test_sendemails_sends_batched_emails_as_bcc(self):
        announcement = Announcement.objects.create(title="Holiday", text="...")
        queue_announcement_emails(announcement)

        output = call_command("sendemails")

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(output, f"Sent 3 emails to {self.user_count} recipients")
        sent_to = []
        for message in mail.outbox:
            self.assertEqual(message.to, [])
            self.assertLessEqual(len(message.bcc), MAX_RECIPIENTS_PER_EMAIL)
            self.assertEqual(message.recipients(), message.bcc)
            # No recipient address appears in the headers
            rendered = message.message()
            self.assertEqual(rendered["To"], UNDISCLOSED_RECIPIENTS)
            self.assertIsNone(rendered["Bcc"])
            self.assertEqual(message.alternatives[0][1], "text/html")
            sent_to.extend(message.bcc)
        self.assertEqual(set(sent_to), self.expected_recipients)
        self.assertFalse(self._announcement_emails().filter(sent=False).exists())

    def test_sendemails_still_sends_per_user_emails(self):
        self.faculty.send_email("Hello", "text body", "<p>html body</p>")

        output = call_command("sendemails")

        self.assertEqual(output, "Sent 1 emails to 1 recipients")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [self.faculty.email])
        self.assertEqual(message.bcc, [])
        self.assertEqual(message.message()["To"], self.faculty.email)
        self.assertTrue(EmailModel.objects.get(receiver=self.faculty.email).sent)

    def test_sendemails_reports_nothing_to_send(self):
        self.assertEqual(call_command("sendemails"), "No emails sent")
        self.assertEqual(len(mail.outbox), 0)
