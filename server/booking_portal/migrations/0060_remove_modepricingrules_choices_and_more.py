# Generated by Django 4.2.9 on 2024-07-20 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0059_remove_facultyrequest_cost_per_sample_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="modepricingrules",
            name="choices",
        ),
        migrations.RemoveField(
            model_name="modepricingrules",
            name="conditional_cost",
        ),
        migrations.RemoveField(
            model_name="modepricingrules",
            name="conditional_text",
        ),
    ]
