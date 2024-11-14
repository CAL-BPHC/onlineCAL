# Generated by Django 4.2.9 on 2024-06-05 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0031_fluorolog3"),
    ]

    operations = [
        migrations.CreateModel(
            name="Fluoromax",
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
                ("sample_codes", models.CharField(max_length=75)),
                ("slot_duration", models.CharField(max_length=75)),
                ("lasers", models.CharField(max_length=75)),
                ("excitation_emission", models.CharField(max_length=75)),
                ("sample_type", models.CharField(max_length=75)),
                ("utilization_of_source", models.CharField(max_length=300)),
                ("additional_info", models.CharField(max_length=300)),
            ],
            options={
                "verbose_name": "Fluoromax",
                "verbose_name_plural": "Fluoromax",
            },
            bases=("booking_portal.userdetail", "booking_portal.userremark"),
        ),
    ]
