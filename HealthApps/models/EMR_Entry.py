"""
file: EMR_Entry.py
description: models for EMR_Entrys
"""

from django.db import models


class EMR_Entry(models.Model):
    """
    EMR_Entry model
    """
    timestamp = models.DateTimeField(blank=True)
    patient = models.ForeignKey('HealthApps.Patient', on_delete=models.DO_NOTHING)

    test = models.ForeignKey('HealthApps.Test', on_delete=models.DO_NOTHING, blank=True, null=True)
    prescription = models.ForeignKey('HealthApps.Prescription', on_delete=models.DO_NOTHING, blank=True, null=True)

    description = models.CharField(max_length=255, blank=True)

    type = models.CharField(max_length=10)

    shown = models.BooleanField(default=False)
