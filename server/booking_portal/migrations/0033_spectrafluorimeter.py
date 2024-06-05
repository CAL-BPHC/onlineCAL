# Generated by Django 4.2.9 on 2024-06-05 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking_portal', '0032_fluoromax'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpectraFluorimeter',
            fields=[
                ('userremark_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='booking_portal.userremark')),
                ('userdetail_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking_portal.userdetail')),
                ('sample_codes', models.CharField(max_length=75)),
                ('slot_duration', models.CharField(max_length=75)),
                ('solvent', models.CharField(max_length=75)),
                ('excitation_emission', models.CharField(max_length=75)),
                ('sample_type', models.CharField(max_length=75)),
                ('utilization_of_source', models.CharField(max_length=300)),
                ('additional_info', models.CharField(max_length=300)),
            ],
            options={
                'verbose_name': 'Spectra Fluorimeter',
                'verbose_name_plural': 'Fluorolog3',
            },
            bases=('booking_portal.userdetail', 'booking_portal.userremark'),
        ),
    ]
