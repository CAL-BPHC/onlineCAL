# Generated by Django 4.2.9 on 2024-09-28 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0063_alter_modepricingrules_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                max_length=75, unique=True, verbose_name="email address"
            ),
        ),
    ]
