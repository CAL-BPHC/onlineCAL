import time

from django.conf import settings
from django.core.management.base import BaseCommand

from ...mail import send_mass_html_mail
from ...models.email import EmailModel

MAX_EMAIL_PER_COMMAND = 30


class Command(BaseCommand):
    help = "Send all queued emails"

    def handle(self, *args, **options):
        print("Sleeping for 60 seconds")
        time.sleep(60)
        print("Slept for 60 seconds")
        emails = EmailModel.objects.filter(sent=False).order_by("date_time")[
            :MAX_EMAIL_PER_COMMAND
        ]
        print(f"Sending {len(emails)} emails")
        start = time.time()
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
            print(email.receiver)
            datatuple.append(message)
            email_objects.append(email)

        sent_count = send_mass_html_mail(datatuple, fail_silently=True)

        end = time.time()
        elapsed = end - start
        print(f"Sent {len(emails)} emails in {elapsed:.2f} seconds")

        start = time.time()
        for email in email_objects[:sent_count]:
            email.sent = True
        EmailModel.objects.bulk_update(email_objects[:sent_count], ["sent"])
        end = time.time()
        elapsed = end - start
        print(f"Updated {len(emails)} emails in {elapsed:.2f} seconds")
