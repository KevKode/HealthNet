"""
file: Log_Item.py
description: models for LogItems
"""

from django.db import models


class LogItem(models.Model):
    """
    Log_Item model
    """
    timestamp = models.DateTimeField()
    description = models.CharField(max_length=30)
    verbose_description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """
        Tostring for LogItem
        :return: timestamp & description
        """
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S") + ": " + self.description
