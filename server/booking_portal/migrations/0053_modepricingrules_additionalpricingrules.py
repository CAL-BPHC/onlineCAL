# Generated by Django 4.2.9 on 2024-07-16 17:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking_portal", "0052_facultyrequest_cost_per_sample_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModePricingRules",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rule_type",
                    models.CharField(
                        choices=[
                            ("FLAT", "Flat Charge"),
                            ("PER_SAMPLE", "Per Sample Charge"),
                            ("PER_TIME_UNIT", "Per Time Unit Charge"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("cost", models.IntegerField(blank=True, default=0, null=True)),
                ("choices", models.JSONField(blank=True, null=True)),
                (
                    "time_in_minutes",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
                ("conditional_text", models.TextField(blank=True, null=True)),
                (
                    "conditional_cost",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
                (
                    "instrument",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking_portal.instrument",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdditionalPricingRules",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rule_type",
                    models.CharField(
                        choices=[
                            ("FLAT", "Flat Charge"),
                            ("PER_SAMPLE", "Per Sample Charge"),
                            ("PER_TIME_UNIT", "Per Time Unit Charge"),
                            ("HELP_TEXT", "Help Text"),
                            ("CHOICE_FIELD", "Choice Field"),
                            ("CONDITIONAL_FIELD", "Conditional Field"),
                            ("ADDITIONAL_FIELD", "Additional Field"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("cost", models.IntegerField(blank=True, default=0, null=True)),
                ("choices", models.JSONField(blank=True, null=True)),
                (
                    "time_in_minutes",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
                ("conditional_text", models.TextField(blank=True, null=True)),
                (
                    "conditional_cost",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
                (
                    "instrument",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="booking_portal.instrument",
                    ),
                ),
            ],
        ),
    ]
