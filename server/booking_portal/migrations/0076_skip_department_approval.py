from django.db import migrations
from django.utils import timezone

WAITING_FOR_LAB_ASST = "R2"
WAITING_FOR_DEPARTMENT = "R6"
DEPARTMENT_APPROVAL = "department_approval"


def move_to_lab_assistant(apps, schema_editor):
    """Take the department's approval as given for upcoming requests.

    They stay billed to the department (needs_department_approval is already
    set), so the lab assistant's approval charges its balance as before.
    update() fires no post_save, so no email goes out for the move.

    Requests whose slot has already passed are left waiting: the department
    never approved them, the session most likely never ran, and moving them
    on would let an approval charge the department for it.
    """
    today = timezone.localdate()
    for name in ("StudentRequest", "FacultyRequest"):
        apps.get_model("booking_portal", name).objects.filter(
            status=WAITING_FOR_DEPARTMENT, slot__date__gte=today
        ).update(status=WAITING_FOR_LAB_ASST)


def drop_queued_department_emails(apps, schema_editor):
    """Unsent "please approve" emails ask for an approval no longer needed."""
    apps.get_model("booking_portal", "EmailModel").objects.filter(
        sent=False, email_type=DEPARTMENT_APPROVAL
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("booking_portal", "0075_alter_emailmodel_subject"),
    ]

    operations = [
        migrations.RunPython(move_to_lab_assistant, migrations.RunPython.noop),
        migrations.RunPython(drop_queued_department_emails, migrations.RunPython.noop),
    ]
