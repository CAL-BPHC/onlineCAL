# Generated by Django 4.2.9 on 2024-06-05 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking_portal', '0033_spectrafluorimeter'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ultracentrifuge',
            fields=[
                ('userremark_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='booking_portal.userremark')),
                ('userdetail_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='booking_portal.userdetail')),
                ('sample_codes', models.CharField(max_length=75)),
                ('slot_duration', models.CharField(max_length=75)),
                ('rotor_used', models.CharField(choices=[('SW-41-Ti', 'SW-41-Ti'), ('70-Ti', '70-Ti'), ('100-Ti', '100-Ti')], max_length=25)),
                ('solvent', models.CharField(max_length=75)),
                ('tubes_used', models.CharField(max_length=75)),
                ('utilization_of_rotor', models.CharField(max_length=300)),
                ('additional_info', models.CharField(max_length=300)),
            ],
            options={
                'verbose_name': 'Ultracentrifuge',
                'verbose_name_plural': 'Ultracentrifuge',
            },
            bases=('booking_portal.userdetail', 'booking_portal.userremark'),
        ),
        migrations.AlterModelOptions(
            name='spectrafluorimeter',
            options={'verbose_name': 'Spectra Fluorimeter', 'verbose_name_plural': 'Spectra Fluorimeter'},
        ),
    ]