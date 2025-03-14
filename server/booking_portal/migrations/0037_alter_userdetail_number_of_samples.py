# Generated by Django 4.2.9 on 2024-06-14 09:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0036_faculty_balance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userdetail",
            name="number_of_samples",
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
    ]
