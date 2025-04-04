# Generated by Django 4.2.9 on 2024-06-15 03:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0039_alter_customuser_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "customuser_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Department",
                "default_related_name": "departments",
            },
            bases=("booking_portal.customuser",),
        ),
    ]
