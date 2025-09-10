from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef
from django.utils.timezone import now

from ...models.faculty_request import FacultyRequest
from ...models.request import StudentRequest
from ...models.slot import Slot


class Command(BaseCommand):
    help = "Delete all Slot records up to yesterday with status 'Empty'"

    def handle(self, *args, **options):
        cutoff_date = now().date() - timedelta(days=30)

        # Delete slots that are:
        # - older than one month ago
        # - currently marked Empty
        # - have never been referenced by any request (no StudentRequest or FacultyRequest rows)

        base_qs = Slot.objects.filter(status=Slot.STATUS_1, date__lte=cutoff_date)
        qs = base_qs.annotate(
            has_student_req=Exists(
                StudentRequest.objects.filter(slot_id=OuterRef("pk"))
            ),
            has_faculty_req=Exists(
                FacultyRequest.objects.filter(slot_id=OuterRef("pk"))
            ),
        ).filter(has_student_req=False, has_faculty_req=False)

        if qs.exists():
            deleted, _ = qs.delete()
            return f"Deleted {deleted} empty slots"

        return f"No empty slots up to {cutoff_date}"
