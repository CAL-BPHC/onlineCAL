# Generated by Django 3.0.2 on 2020-12-23 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="slot",
            old_name="slot_name",
            new_name="slot_duration",
        ),
        migrations.AlterField(
            model_name="slot",
            name="time",
            field=models.TimeField(),
        ),
    ]
