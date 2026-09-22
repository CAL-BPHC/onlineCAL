import datetime

from django.db import migrations, transaction
from django.utils import timezone

WAITING_FOR_LAB_ASST = "R2"
APPROVED = "R3"
WAITING_FOR_DEPARTMENT = "R6"
DEPARTMENT_APPROVAL = "department_approval"
# The lab assistant keeps the last week's requests to decide on as usual.
LAB_KEEPS = datetime.timedelta(days=7)


def move_to_lab_assistant(apps, schema_editor):
    """Take the department's approval as given for everything waiting on it.

    They stay billed to the department (needs_department_approval is already
    set), so the lab assistant's approval charges its balance as before.
    update() fires no post_save, so no email goes out for the move.
    """
    for name in ("StudentRequest", "FacultyRequest"):
        apps.get_model("booking_portal", name).objects.filter(
            status=WAITING_FOR_DEPARTMENT
        ).update(status=WAITING_FOR_LAB_ASST)


def _lab_assistant_accept(request_obj):
    """views/user/lab_assistant.py:lab_assistant_accept, minus the HTTP.

    Charges whoever the request is billed to and approves it. Saving runs the
    post_save signals, which mark the slot filled.
    """
    if request_obj.needs_department_approval:
        payer = request_obj.faculty.department
    else:
        payer = request_obj.faculty
    payer.balance -= request_obj.total_cost
    payer.save()
    request_obj.status = APPROVED
    request_obj.save()


def approve_old_lab_requests(apps, schema_editor):
    """Approve what has waited on the lab assistant for over a week.

    The sessions ran; only the approvals were never given. Each is charged
    exactly as the lab assistant's approval would have charged it, and nobody
    is emailed about it. The last week's requests stay with the lab assistant.

    Cost and the slot update live on the real models and their signals, which
    the historical models a migration normally uses do not have. The real
    models are only touched when there is something to approve, so a fresh or
    test database, whose tables are empty, never meets a model newer than this
    migration.
    """
    cutoff = timezone.localdate() - LAB_KEEPS
    if not any(
        apps.get_model("booking_portal", name)
        .objects.filter(status=WAITING_FOR_LAB_ASST, slot__date__lt=cutoff)
        .exists()
        for name in ("StudentRequest", "FacultyRequest")
    ):
        return

    from booking_portal.models import CustomUser, FacultyRequest, StudentRequest
    from booking_portal.models.email import EmailModel

    send_email = CustomUser.send_email
    CustomUser.send_email = lambda self, *args, **kwargs: None
    try:
        with transaction.atomic():
            emails = EmailModel.objects.count()
            for model in (StudentRequest, FacultyRequest):
                for pk in (
                    model.objects.filter(
                        status=WAITING_FOR_LAB_ASST, slot__date__lt=cutoff
                    )
                    .order_by("pk")
                    .values_list("pk", flat=True)
                ):
                    # read each fresh, so no balance is charged off a stale copy
                    _lab_assistant_accept(
                        model.objects.select_related("faculty__department").get(pk=pk)
                    )
            if EmailModel.objects.count() != emails:
                raise RuntimeError("Approving old lab requests queued emails")
    finally:
        CustomUser.send_email = send_email


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
        migrations.RunPython(approve_old_lab_requests, migrations.RunPython.noop),
        migrations.RunPython(drop_queued_department_emails, migrations.RunPython.noop),
    ]
