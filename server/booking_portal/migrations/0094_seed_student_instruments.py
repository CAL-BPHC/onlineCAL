import datetime

from django.db import migrations
from django.db.models import Count, Max, Q
from django.utils import timezone

APPROVED = "R3"
# One booking this long ago says little about whether the student still uses
# the instrument; they can ask to be assigned it again.
ONE_OFF_LAPSES_AFTER = datetime.timedelta(days=365)


def assign_approved_instruments(apps, schema_editor):
    """Let every existing student keep booking what they were approved for.

    A student is assigned each instrument they have an approved request for,
    unless that was a single booking more than a year ago. A request that
    never got approved, whether still pending, rejected or cancelled, assigns
    nothing.
    """
    Student = apps.get_model("booking_portal", "Student")
    StudentRequest = apps.get_model("booking_portal", "StudentRequest")
    Assignment = Student.instruments.through
    cutoff = timezone.localdate() - ONE_OFF_LAPSES_AFTER
    approved = (
        StudentRequest.objects.filter(status=APPROVED)
        .values("student_id", "instrument_id")
        .annotate(bookings=Count("id"), last=Max("slot__date"))
        .filter(Q(bookings__gt=1) | Q(last__gte=cutoff))
    )
    Assignment.objects.bulk_create(
        (
            Assignment(student_id=row["student_id"], instrument_id=row["instrument_id"])
            for row in approved
        ),
        # reversing this migration keeps the rows, so it may run over them
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("booking_portal", "0093_student_instruments"),
    ]

    operations = [
        migrations.RunPython(assign_approved_instruments, migrations.RunPython.noop),
    ]
