from django.db import migrations

APPROVED = "R3"


def assign_approved_instruments(apps, schema_editor):
    """Let every existing student keep booking what they were approved for.

    A student is assigned each instrument they have an approved request for.
    A request that never got approved, whether still pending, rejected or
    cancelled, assigns nothing.
    """
    Student = apps.get_model("booking_portal", "Student")
    StudentRequest = apps.get_model("booking_portal", "StudentRequest")
    Assignment = Student.instruments.through
    approved = (
        StudentRequest.objects.filter(status=APPROVED)
        .values_list("student_id", "instrument_id")
        .distinct()
    )
    Assignment.objects.bulk_create(
        (
            Assignment(student_id=student_id, instrument_id=instrument_id)
            for student_id, instrument_id in approved
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
