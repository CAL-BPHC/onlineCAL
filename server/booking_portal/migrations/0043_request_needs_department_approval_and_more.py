# Generated by Django 4.2.9 on 2024-06-15 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0042_department_balance"),
    ]

    operations = [
        migrations.AddField(
            model_name="request",
            name="needs_department_approval",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="request",
            name="status",
            field=models.CharField(
                choices=[
                    ("R1", "Waiting for faculty approval."),
                    ("R2", "Waiting for lab assistant approval."),
                    ("R3", "Approved"),
                    ("R4", "Rejected"),
                    ("R5", "Cancelled"),
                    ("R6", "Waiting for department approval"),
                ],
                max_length=50,
            ),
        ),
    ]
