# Generated by Django 4.2.20 on 2025-07-23 14:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0067_icpms_elements"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="icpms",
            name="calibration_solution_concentration",
        ),
        migrations.RemoveField(
            model_name="icpms",
            name="digestion_carried_out",
        ),
        migrations.RemoveField(
            model_name="icpms",
            name="elements",
        ),
        migrations.RemoveField(
            model_name="icpms",
            name="method",
        ),
        migrations.RemoveField(
            model_name="icpms",
            name="sample_filtered",
        ),
        migrations.AlterField(
            model_name="icpms",
            name="target_elements_concentration",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(200),
                    django.core.validators.MinValueValidator(1),
                ]
            ),
        ),
    ]
