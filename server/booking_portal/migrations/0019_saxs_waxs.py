# Generated by Django 3.2.11 on 2022-01-10 16:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0018_alter_utm_test_speed"),
    ]

    operations = [
        migrations.CreateModel(
            name="SAXS_WAXS",
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
                (
                    "nature_of_samples",
                    models.CharField(
                        choices=[
                            ("Film", "Film"),
                            ("Liquid", "Liquid"),
                            ("Powder", "Powder"),
                            ("Other", "Other"),
                        ],
                        max_length=10,
                    ),
                ),
            ],
            options={
                "verbose_name": "SAXS/WAXS",
                "verbose_name_plural": "SAXS/WAXS",
            },
            bases=("booking_portal.userdetail", "booking_portal.userremark"),
        ),
    ]
