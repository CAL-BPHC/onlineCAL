import contextlib
import smtplib
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


def connection_lost(error):
    """
    Whether the connection broke while sending, as opposed to the mail server
    refusing the email. When it breaks we cannot know if the email went out.
    """
    if isinstance(error, smtplib.SMTPServerDisconnected):
        return True
    return isinstance(error, OSError) and not isinstance(error, smtplib.SMTPException)


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

        connection = get_connection()
        try:
            connection.open()
        except OSError:
            return "No emails sent: could not connect to the mail server"

        sent_emails = []
        try:
            for email in emails:
                if time.monotonic() - started > MAX_SECONDS_PER_COMMAND:
                    break
                # Claim the email (mark it as sent) *before* sending it. The
                # claim is atomic, so an overlapping run of this command can
                # never send the same email again. A batched email goes to a
                # hundred people and takes a while to send, so runs do overlap.
                if not self._set_sent(email, was=False, to=True):
                    continue
                try:
                    sent = send_mass_html_mail(
                        [self._message(email)], connection=connection
                    )
                except (OSError, ValueError) as error:
                    # SMTP errors are OSErrors; a ValueError is a bad header
                    if not connection_lost(error):
                        self._set_sent(email, was=True, to=False)
                        continue
                    # We don't know whether the email went out. Retry an email
                    # to one person, but never risk repeating a batched one.
                    if email.recipient_count == 1:
                        self._set_sent(email, was=True, to=False)
                    break
                if sent:
                    sent_emails.append(email)
                else:
                    self._set_sent(email, was=True, to=False)
        finally:
            with contextlib.suppress(OSError):
                connection.close()

        if not sent_emails:
            return "No emails sent"
        recipient_count = sum(email.recipient_count for email in sent_emails)
        return f"Sent {len(sent_emails)} emails to {recipient_count} recipients"

    @staticmethod
    def _set_sent(email, was, to):
        """Atomically flip `sent`. Returns whether this call made the change."""
        return EmailModel.objects.filter(pk=email.pk, sent=was).update(sent=to) == 1

    @staticmethod
    def _message(email):
        return (
            email.subject,
            email.text,
            email.text_html,
            settings.EMAIL_HOST_USER,
            [email.receiver] if email.receiver else [],
            email.bcc_list,
        )
