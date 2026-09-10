from django.conf import settings
from django.core.management.base import BaseCommand

from ...mail import send_mass_html_mail
from ...models.email import EmailModel

MAX_EMAIL_PER_COMMAND = 30


class Command(BaseCommand):
    help = "Send all queued emails"

    def handle(self, *args, **options):
        emails = EmailModel.objects.filter(sent=False).order_by("date_time")[
            :MAX_EMAIL_PER_COMMAND
        ]
        datatuple = []
        email_objects = []
        for email in emails:
            message = (
                email.subject,
                email.text,
                email.text_html,
                settings.EMAIL_HOST_USER,
                [email.receiver] if email.receiver else [],
                email.bcc_list,
            )
            datatuple.append(message)
            email_objects.append(email)

        sent_count = send_mass_html_mail(datatuple, fail_silently=True)
        sent_emails = email_objects[:sent_count]
        for email in sent_emails:
            email.sent = True
        EmailModel.objects.bulk_update(sent_emails, ["sent"])

        if sent_count > 0:
            recipient_count = sum(email.recipient_count for email in sent_emails)
            return f"Sent {sent_count} emails to {recipient_count} recipients"
        else:
            return "No emails sent"
