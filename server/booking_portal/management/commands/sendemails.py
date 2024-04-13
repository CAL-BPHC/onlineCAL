from django.conf import settings
from django.core.management.base import BaseCommand
import time

from ...mail import send_mass_html_mail
from ...models.email import EmailModel

MAX_EMAIL_PER_COMMAND = 30


class Command(BaseCommand):
    help = 'Send all queued emails'

    def handle(self, *args, **options):
        print('Sleeping for 60 seconds')
        time.sleep(60)
        print('Slept for 60 seconds')
        emails = EmailModel.objects.filter(sent=False).order_by('date_time')[
            :MAX_EMAIL_PER_COMMAND]
        print(f'Sending {len(emails)} emails')
        start = time.time()
        datatuple = []
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
            email.sent = True
        send_mass_html_mail(datatuple, fail_silently=False)

        end = time.time()
        elapsed = end - start
        print(f'Sent {len(emails)} emails in {elapsed:.2f} seconds')

        start = time.time()
        EmailModel.objects.bulk_update(emails, ['sent'])
        end = time.time()
        elapsed = end - start
        print(f'Updated {len(emails)} emails in {elapsed:.2f} seconds')
