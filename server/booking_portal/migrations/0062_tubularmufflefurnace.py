# Generated by Django 4.2.9 on 2024-08-30 10:23

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0061_freezedryer"),
    ]

    operations = [
        migrations.CreateModel(
            name="TubularMuffleFurnace",
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
                    "sample_nature",
                    models.CharField(
                        choices=[("Powder", "Powder"), ("Film", "Film")], max_length=10
                    ),
                ),
                ("temperature", models.IntegerField()),
                (
                    "quantity",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
            ],
            options={
                "verbose_name": "Tubular/Muffle Furnace",
                "verbose_name_plural": "Tubular/Muffle Furnace",
            },
            bases=("booking_portal.userdetail", "booking_portal.userremark"),
        ),
    ]
