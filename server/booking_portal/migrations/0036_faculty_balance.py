# Generated by Django 4.2.9 on 2024-06-14 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_portal', '0035_instrument_cost_per_sample'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]
