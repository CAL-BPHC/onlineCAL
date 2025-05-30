# Generated by Django 4.2.9 on 2024-06-15 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("booking_portal", "0044_rename_request_studentrequest"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacultyRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("R2", "Waiting for lab assistant approval."),
                            ("R3", "Approved"),
                            ("R4", "Rejected"),
                            ("R5", "Cancelled"),
                            ("R6", "Waiting for department approval"),
                        ],
                        max_length=50,
                    ),
                ),
                ("needs_department_approval", models.BooleanField(default=False)),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="booking_portal.faculty",
                    ),
                ),
                (
                    "instrument",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="booking_portal.instrument",
                    ),
                ),
                (
                    "lab_assistant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="booking_portal.labassistant",
                    ),
                ),
                (
                    "slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking_portal.slot",
                    ),
                ),
            ],
        ),
    ]
