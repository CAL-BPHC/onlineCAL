# Generated by Django 3.0.2 on 2021-01-30 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_portal', '0010_auto_20210123_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='number_of_samples',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]