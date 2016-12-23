"""
file: Test.py
description: models for Tests
"""

from django.db import models


class Test(models.Model):
    """
    Test model
    """
    timestamp = models.DateTimeField()
    patient = models.ForeignKey('HealthApps.Patient', on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey('HealthApps.Doctor', on_delete=models.DO_NOTHING)
    hospital = models.ForeignKey('HealthApps.Hospital', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    file = models.FileField(upload_to="Electronic_Medical_Record/%Y/%m/%d", blank=True)
    filename = models.CharField(max_length=30, blank=True)
    released = models.BooleanField(default=False)


