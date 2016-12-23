"""
file: Nurse.py
description: models for Nurses
"""

from django.db import models
from django.contrib.auth.models import User


class Nurse(models.Model):
    """
    Nurse model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospitals = models.ManyToManyField('HealthApps.Hospital', blank=True)
    doctors = models.ManyToManyField('HealthApps.Doctor', blank=True)

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
        return "nurse"