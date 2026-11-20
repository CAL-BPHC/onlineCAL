from django.db import migrations

REJECTED = "R4"
CANCELLED = "R5"


def assign_booked_instruments(apps, schema_editor):
    """Let every existing student keep booking what they already book.

    A student is assigned each instrument they have a request for, unless the
    request was rejected or cancelled: those never took place.
    """
    Student = apps.get_model("booking_portal", "Student")
    StudentRequest = apps.get_model("booking_portal", "StudentRequest")
    Assignment = Student.instruments.through
    booked = (
        StudentRequest.objects.exclude(status__in=(REJECTED, CANCELLED))
        .values_list("student_id", "instrument_id")
        .distinct()
    )
    Assignment.objects.bulk_create(
        (
            Assignment(student_id=student_id, instrument_id=instrument_id)
            for student_id, instrument_id in booked
        ),
        # reversing this migration keeps the rows, so it may run over them
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("booking_portal", "0093_student_instruments"),
    ]

    operations = [
        migrations.RunPython(assign_booked_instruments, migrations.RunPython.noop),
    ]
