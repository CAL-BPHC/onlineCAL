# Generated by Django 4.2.9 on 2024-06-29 07:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0050_alter_balancetopuplog_top_up_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="facultyrequest",
            name="student",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="booking_portal.student",
            ),
        ),
    ]
