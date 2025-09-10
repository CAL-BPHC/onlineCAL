from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import localdate

from ...models.email import EmailModel


class Command(BaseCommand):
    help = "Delete all EmailModel records up to one month ago with email_type 'new_announcement'"

    def handle(self, *args, **options):
        today = localdate()
        cutoff_date = today - timedelta(days=30)

        # Delete emails that are:
        # - marked as sent
        # - older than one month ago
        # - of type new_announcement
        qs = EmailModel.objects.filter(
            sent=True,
            email_type=EmailModel.NEW_ANNOUNCEMENT,
            date_time__date__lte=cutoff_date,
        )

        if qs.exists():
            deleted, _ = qs.delete()
            return f"Deleted {deleted} new announcement emails older than {cutoff_date}"

        return f"No new announcement emails found older than {cutoff_date}"
