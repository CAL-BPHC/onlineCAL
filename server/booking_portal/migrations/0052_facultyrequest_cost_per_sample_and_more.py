# Generated by Django 4.2.9 on 2024-06-30 10:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0051_facultyrequest_student"),
    ]

    operations = [
        migrations.AddField(
            model_name="facultyrequest",
            name="cost_per_sample",
            field=models.IntegerField(
                default=0, validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AddField(
            model_name="studentrequest",
            name="cost_per_sample",
            field=models.IntegerField(
                default=0, validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
    ]
