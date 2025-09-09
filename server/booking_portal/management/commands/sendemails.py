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
                [email.receiver],
            )
            datatuple.append(message)
            email_objects.append(email)

        sent_count = send_mass_html_mail(datatuple, fail_silently=True)
        for email in email_objects[:sent_count]:
            email.sent = True
        EmailModel.objects.bulk_update(email_objects[:sent_count], ["sent"])

        if sent_count > 0:
            return f"Sent {sent_count} emails to {', '.join([email.receiver for email in email_objects[:sent_count]])}"
        else:
            return "No emails sent"
