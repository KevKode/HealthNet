"""
file: Hospital_Admin.py
description: models for Hospital_Admins
"""

from django.db import models
from django.contrib.auth.models import User


class Hospital_Admin(models.Model):
    """
    Hospital_Admin model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey('HealthApps.Hospital', on_delete=models.DO_NOTHING)

    def __str__(self):
        """
        Tostring for Hospital_Admin
        :return: full name
        """
        return self.user.first_name + " " + self.user.last_name

    def get_type(self):
        """
        Returns user type
        :return: user type
        """
        return "admin"
