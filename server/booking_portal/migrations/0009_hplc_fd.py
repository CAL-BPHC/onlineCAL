# Generated by Django 3.0.2 on 2021-01-23 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking_portal', '0008_userdetail_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='HPLC_FD',
            fields=[
                ('userremark_ptr', models.OneToOneField(auto_created=True,
                 on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='booking_portal.UserRemark')),
                ('userdetail_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE,
                 parent_link=True, primary_key=True, serialize=False, to='booking_portal.UserDetail')),
                ('sample_code', models.CharField(max_length=75)),
                ('sample_information', models.CharField(max_length=75)),
                ('mobile_phase', models.CharField(max_length=75)),
                ('column_for_lc', models.CharField(max_length=75)),
                ('detection_wavelength', models.CharField(max_length=75)),
            ],
            options={'verbose_name': 'HPLC-FD',
                     'verbose_name_plural': 'HPLC-FD'},
            bases=('booking_portal.userdetail',
                   'booking_portal.userremark', models.Model),
        ),
    ]
