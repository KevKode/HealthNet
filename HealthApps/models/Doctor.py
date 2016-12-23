"""
file: Doctor.py
description: models for Doctors
"""

from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    """
    Doctor model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospitals = models.ManyToManyField('HealthApps.Hospital', blank=True)
    max_patients = models.PositiveIntegerField()
    cur_patients = models.PositiveIntegerField(default=0)

    def __str__(self):
        """
        Tostring for Doctor
        :return: full name
        """
        return self.user.first_name + " " + self.user.last_name

    def get_type(self):
        """
        Returns user type
        :return: user type
        """
        return "doctor"
