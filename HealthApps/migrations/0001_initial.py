# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-12-05 03:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('description', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_patients', models.PositiveIntegerField()),
                ('cur_patients', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EMR_Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(max_length=10)),
                ('shown', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Hospital_Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Hospital')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('description', models.CharField(max_length=30)),
                ('verbose_description', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Nurse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctors', models.ManyToManyField(blank=True, to='HealthApps.Doctor')),
                ('hospitals', models.ManyToManyField(blank=True, to='HealthApps.Hospital')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insurance_number', models.CharField(max_length=13)),
                ('emergency_name', models.CharField(max_length=30)),
                ('emergency_number', models.CharField(max_length=30)),
                ('height', models.FloatField(blank=True, null=True)),
                ('weight', models.FloatField(blank=True, null=True)),
                ('cholesterol', models.CharField(blank=True, max_length=30, null=True)),
                ('pulse', models.PositiveIntegerField(blank=True, null=True)),
                ('temperature', models.FloatField(blank=True, null=True)),
                ('blood_pressure', models.CharField(blank=True, max_length=30, null=True)),
                ('blood_type', models.CharField(choices=[('O', 'O'), ('A', 'A'), ('B', 'B'), ('AB', 'AB')], max_length=30)),
                ('admitted_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='HealthApps.Hospital')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Doctor')),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Hospital')),
                ('transfer_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='HealthApps.Hospital')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('name', models.CharField(max_length=30)),
                ('dosage_amount', models.PositiveIntegerField()),
                ('dosage_unit', models.CharField(blank=True, choices=[('tablets', 'tablets'), ('mL', 'mL')], max_length=10)),
                ('frequency_amount', models.PositiveIntegerField()),
                ('frequency_unit', models.CharField(choices=[('per hour', 'per hour'), ('per day', 'per day'), ('per week', 'per week'), ('per doctor instruction', 'per doctor instructions')], max_length=30)),
                ('prescribed', models.BooleanField(default=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=255)),
                ('file', models.FileField(blank=True, upload_to='Electronic_Medical_Record/%Y/%m/%d')),
                ('filename', models.CharField(blank=True, max_length=30)),
                ('released', models.BooleanField(default=False)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Doctor')),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Hospital')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Patient')),
            ],
        ),
        migrations.AddField(
            model_name='hospital',
            name='admitted_patients',
            field=models.ManyToManyField(blank=True, related_name='_hospital_admitted_patients_+', to='HealthApps.Patient'),
        ),
        migrations.AddField(
            model_name='emr_entry',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Patient'),
        ),
        migrations.AddField(
            model_name='emr_entry',
            name='prescription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Prescription'),
        ),
        migrations.AddField(
            model_name='emr_entry',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Test'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='hospitals',
            field=models.ManyToManyField(blank=True, to='HealthApps.Hospital'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Hospital'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='HealthApps.Patient'),
        ),
    ]
