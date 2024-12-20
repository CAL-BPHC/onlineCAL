# Generated by Django 4.2.9 on 2024-06-15 04:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0040_department"),
    ]

    operations = [
        migrations.AlterField(
            model_name="faculty",
            name="department",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="booking_portal.department",
            ),
        ),
    ]
