# Generated by Django 3.0.2 on 2021-02-07 05:08
from datetime import datetime, timedelta

from django.db import migrations, models


def calc_end_time_from_duration(apps, schema_editor):
    slot_model = apps.get_model("booking_portal", "slot")
    now_date = datetime.now().date()

    for slot in slot_model.objects.all():
        duration = slot.duration
        if duration:
            duration = datetime.strptime(duration, "%H:%M:%S")
            duration = timedelta(
                hours=duration.hour, minutes=duration.minute, seconds=duration.second
            )
            slot.end_time = (
                datetime.combine(now_date, slot.start_time) + duration
            ).time()
            slot.save()


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("booking_portal", "0011_userdetail_number_of_samples"),
    ]

    operations = [
        migrations.RenameField(
            model_name="slot",
            old_name="time",
            new_name="start_time",
        ),
        migrations.AddField(
            model_name="slot",
            name="end_time",
            field=models.TimeField(default=datetime.now().time()),
            preserve_default=False,
        ),
        migrations.RunPython(
            calc_end_time_from_duration,
        ),
        migrations.RemoveField(
            model_name="slot",
            name="duration",
        ),
    ]
