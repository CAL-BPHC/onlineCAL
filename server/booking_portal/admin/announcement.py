from booking_portal.mail import MAX_RECIPIENTS_PER_EMAIL
from booking_portal.models import CustomUser
from booking_portal.models.email import EmailModel
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse


def queue_announcement_emails(announcement):
    """
    Notify every active user about a new announcement.

    The email body is the same for everyone, so instead of one email per user
    we queue one email per batch of recipients, with the recipients in BCC.
    This keeps an announcement well within Gmail's daily message quota.
    Returns the number of emails queued.
    """
    email_type = EmailModel.NEW_ANNOUNCEMENT
    context = {
        "announcement_title": announcement.title,
        "announcement_text": announcement.text,
        "announcement_url": "https://onlinecif.bits-hyderabad.ac.in"
        + reverse("announcements"),
    }
    text = render_to_string("email/new_announcement.txt", context)
    text_html = render_to_string("email/new_announcement.html", context)

    recipients = list(
        CustomUser.objects.filter(is_active=True)
        # Skip sending announcements to test users
        .exclude(email__endswith="@email.com")
        .order_by("email")
        .values_list("email", flat=True)
    )

    emails = [
        EmailModel(
            receiver=None,
            bcc=",".join(recipients[start : start + MAX_RECIPIENTS_PER_EMAIL]),
            subject=f"New CIF Announcement: {announcement.title}",
            text=text,
            text_html=text_html,
            sent=False,
            email_type=email_type,
        )
        for start in range(0, len(recipients), MAX_RECIPIENTS_PER_EMAIL)
    ]
    EmailModel.objects.bulk_create(emails)
    return len(emails)


class AnnouncementAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        queue_announcement_emails(obj)
        return super().response_add(request, obj, post_url_continue)
