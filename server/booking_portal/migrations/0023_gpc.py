# Generated by Django 4.2.9 on 2024-05-26 07:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0022_epr_esr"),
    ]

    operations = [
        migrations.CreateModel(
            name="GPC",
            fields=[
                (
                    "userremark_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        to="booking_portal.userremark",
                    ),
                ),
                (
                    "userdetail_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="booking_portal.userdetail",
                    ),
                ),
                ("sample_code", models.CharField(max_length=75)),
                ("solvent_column", models.CharField(max_length=100)),
                ("parameters", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "GPC",
                "verbose_name_plural": "GPC",
            },
            bases=("booking_portal.userdetail", "booking_portal.userremark"),
        ),
    ]
