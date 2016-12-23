"""
file: Patient.py
description: models for Patients
"""

from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    """
    Patient model
    """
    insurance_number = models.CharField(max_length=13)
    hospital = models.ForeignKey('HealthApps.Hospital', on_delete=models.DO_NOTHING)
    admitted_to = models.ForeignKey('HealthApps.Hospital', on_delete=models.DO_NOTHING, related_name='+', null=True,
                                    blank=True)
    doctor = models.ForeignKey('HealthApps.Doctor', on_delete=models.DO_NOTHING)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    emergency_name = models.CharField(max_length=30)
    emergency_number = models.CharField(max_length=30)

    transfer_to = models.ForeignKey('HealthApps.Hospital', on_delete=models.DO_NOTHING, related_name='+', null=True,
                                    blank=True)
    height = models.FloatField(blank=True, null=True)  # Measured in inches | min: 6, max: 108
    weight = models.FloatField(blank=True, null=True)  # Measured in pounds | min: 0.5, max: 1500
    cholesterol = models.CharField(max_length=30, blank=True,
                                   null=True)  # Measured in mg/dL, X/X LDL/HDL | min: 90/25 max: 200/100
    pulse = models.PositiveIntegerField(blank=True, null=True)  # Measured in BPM | min: 25, max: 250
    temperature = models.FloatField(blank=True, null=True)  # Measured in Fahrenheit | min: 55, max: 120
    blood_pressure = models.CharField(max_length=30, blank=True,
                                      null=True)  # Measured in systolic/diastolic mm Hg | min: 100/60, max: 180/120

    blood_types = (('O', 'O'),
                   ('A', 'A'),
                   ('B', 'B'),
                   ('AB', 'AB'))
    blood_type = models.CharField(max_length=30, choices=blood_types)

    def __str__(self):
        """
        Tostring for patient
        :return: full name
        """
        return self.user.first_name + " " + self.user.last_name

    def get_type(self):
        """
        Returns user type
        :return: user type
        """
        return 'patient'
