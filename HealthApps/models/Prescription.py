"""
file: Prescription.py
description: models for Prescriptions
"""


from django.db import models


class Prescription(models.Model):
    """
    Prescription model
    """
    timestamp = models.DateTimeField()
    patient = models.ForeignKey('HealthApps.Patient', on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey('HealthApps.Doctor', on_delete=models.DO_NOTHING)

    name = models.CharField(max_length=30)
    dosage_amount = models.PositiveIntegerField()
    dosage_choices = (('tablets', 'tablets'),
                      ('mL', 'mL'))
    dosage_unit = models.CharField(max_length=10, choices=dosage_choices, blank=True)
    frequency_amount = models.PositiveIntegerField()
    frequencies = (('per hour', 'per hour'),
                   ('per day', 'per day'),
                   ('per week', 'per week'),
                   ('per doctor instruction', 'per doctor instructions'))
    frequency_unit = models.CharField(max_length=30, choices=frequencies)
    prescribed = models.BooleanField(default=True)
