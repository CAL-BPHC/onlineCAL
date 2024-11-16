# Generated by Django 3.2.5 on 2021-09-08 10:11

import django.db.models.deletion
from django.db import migrations, models


def create_instruments(apps, schema_editor):
    instrument_model = apps.get_model("booking_portal", "Instrument")
    instrument_model.objects.create(
        pk=21,
        name="UTM",
        desc="Universal Testing Machine",
        status=False,
    )


def delete_instruments(apps, schema_editor):
    instrument_model = apps.get_model("booking_portal", "Instrument")
    instrument_model.objects.filter(pk=21).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0012_auto_20210207_1038"),
    ]

    operations = [
        migrations.CreateModel(
            name="UTM",
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
                ("material", models.CharField(max_length=75)),
                (
                    "test_type",
                    models.CharField(
                        choices=[
                            ("tensile", "Tensile"),
                            ("compression", "Compression"),
                            ("3-point-bending", "3 Point Bending"),
                            ("ilss", "ILSS"),
                            ("double-cant-beam", "Double Cantilever Beam"),
                        ],
                        max_length=75,
                    ),
                ),
                ("test_speed", models.IntegerField()),
                (
                    "temperature",
                    models.IntegerField(
                        help_text="Ranges:Room Temperature = 25°CTemperature Chamber = -70°C - 250°CFurnace = 250°C - 1200°CAny additional remarks can be specified in the box below."
                    ),
                ),
            ],
            bases=("booking_portal.userdetail", "booking_portal.userremark"),
        ),
        migrations.RunPython(create_instruments, delete_instruments),
    ]
