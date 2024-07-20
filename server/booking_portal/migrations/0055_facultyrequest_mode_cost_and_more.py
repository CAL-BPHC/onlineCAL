# Generated by Django 4.2.9 on 2024-07-17 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_portal', '0054_studentrequest_mode_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='facultyrequest',
            name='mode_cost',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='facultyrequest',
            name='mode_description',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]