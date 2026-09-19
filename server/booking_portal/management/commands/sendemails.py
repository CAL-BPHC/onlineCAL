import time

from django.conf import settings
from django.core.mail import get_connection
from django.core.management.base import BaseCommand

from ...mail import send_mass_html_mail
from ...models.email import EmailModel

MAX_EMAIL_PER_COMMAND = 30

# This command is scheduled every minute. Stop picking up new emails after this
# long, so that runs don't pile up and never reach the Django Q task timeout.
MAX_SECONDS_PER_COMMAND = 45


class Command(BaseCommand):
    help = "Send all queued emails"

    def handle(self, *args, **options):
        started = time.monotonic()
        emails = list(
            EmailModel.objects.filter(sent=False).order_by("date_time")[
                :MAX_EMAIL_PER_COMMAND
            ]
        )
        if not emails:
            return "No emails sent"

        sent_emails = []
        connection = get_connection(fail_silently=True)
        connection.open()
        try:
            for email in emails:
                if time.monotonic() - started > MAX_SECONDS_PER_COMMAND:
                    break
                if self._send(email, connection):
                    sent_emails.append(email)
        finally:
            connection.close()

        if not sent_emails:
            return "No emails sent"
        recipient_count = sum(email.recipient_count for email in sent_emails)
        return f"Sent {len(sent_emails)} emails to {recipient_count} recipients"

    @staticmethod
    def _send(email, connection):
        """
        Send one queued email. Returns whether it was sent.

        The email is claimed (marked as sent) *before* it is sent, and the claim
        is atomic, so an overlapping run of this command can never send the same
        email again. A batched email goes to a hundred people and takes a while
        to send, so runs do overlap.
        """
        claimed = EmailModel.objects.filter(pk=email.pk, sent=False).update(sent=True)
        if not claimed:
            return False

        message = (
            email.subject,
            email.text,
            email.text_html,
            settings.EMAIL_HOST_USER,
            [email.receiver] if email.receiver else [],
            email.bcc_list,
        )
        try:
            sent = send_mass_html_mail([message], connection=connection) == 1
        except (OSError, ValueError):
            # A network error (SMTP errors included) or an unsendable message
            sent = False
        if not sent:
            # Release the claim so that a later run retries this email
            EmailModel.objects.filter(pk=email.pk).update(sent=False)
        return sent
