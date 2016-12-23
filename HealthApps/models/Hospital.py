"""
file: Hospital.py
description: models for Hospitals
"""

from django.db import models


class Hospital(models.Model):
    """
    Hospital model
    """
    name = models.CharField(max_length=30)
    admitted_patients = models.ManyToManyField('HealthApps.Patient', related_name='+', blank=True)

    def __str__(self):
        """
        Tostring for Hospital
        :return: name
        """
        return self.name
