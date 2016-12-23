"""
file: Appointment.py
description: models for Appointments
"""

from django.db import models
import datetime
import time


class Appointment(models.Model):
    """
    Appointment model
    """
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=500, null=True)
    hospital = models.ForeignKey('HealthApps.Hospital', on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey('HealthApps.Doctor', on_delete=models.DO_NOTHING)
    patient = models.ForeignKey('HealthApps.Patient', on_delete=models.DO_NOTHING, null = True)

    def __str__(self):
        """
        Tostring for Appointment
        :return: appointment description
        """
        if self.patient != None:
            return "Appointment with Dr." + self.doctor.user.last_name + " and " + self.patient.user.first_name + " " + self.patient.user.last_name
        else:
            return "Appointment with Dr." + self.doctor.user.last_name

    def conflict_checker(self, hospital, date, start_time, end_time, old_appointment):
        """
        Determines whether there is a scheduling conflict
        :param hospital: specific hospital
        :param date: specific date
        :param start_time: specific starting time
        :param end_time: specific ending time
        :param old_appointment: old appointment
        :return: whether or not it conflicts
        """
        doctor = self
        result = [True, "no message"]
        if datetime.datetime.combine(date, start_time) < datetime.datetime.now():
            result[0] = False
            result[1] = "Sorry, you cannot create appointments set in the past. Please try again."
        elif (datetime.datetime(100,1,1,start_time.hour, start_time.minute,00) + datetime.timedelta(minutes=30)).time() > end_time:
            result[0] = False
            result[1] = "Sorry, you cannot create appointments less than thirty minutes. Please try again."
        else:
            for app in Appointment.objects.all():
                if (date == app.date) and (doctor == app.doctor) and (
                            (old_appointment is not None and old_appointment.pk != app.pk) or old_appointment is None):
                    if start_time == app.start_time:
                        result[0] = False
                        result[1] = "Sorry, another appointment starts at that time. Please try again."
                    elif (start_time < app.start_time) and (end_time > app.start_time):
                        result[0] = False
                        result[1] = "Sorry, that time was taken. Please try again."
                    elif (start_time > app.start_time) and (start_time < app.end_time):
                        result[0] = False
                        result[1] = "Sorry, that time was taken. Please try again."
                    # check for if start_time is within ten minutes of another appointment's end_time
                    elif app.end_time < start_time and (datetime.datetime(100,1,1,start_time.hour, start_time.minute,00) - datetime.timedelta(minutes=10)).time() < app.end_time:
                        result[0] = False
                        result[1] = "Sorry, the appointment starts too soon to the end of another appointment. Please try again."
                    # check for if end_time is within ten minutes of another appointment's start_time
                    elif end_time < app.start_time and (datetime.datetime(100, 1, 1, end_time.hour, end_time.minute, 00) + datetime.timedelta(minutes=10)).time() > app.start_time:
                        result[0] = False
                        result[1] = "Sorry, the appointment ends too soon to the start of another appointment. Please try again."
                    # check for if doctor is in that hospital on that day
                    elif hospital != app.hospital:
                        result[0] = False
                        result[1] = "Sorry, the doctor is in a different hospital on that date. Please try again."
        return result

    def time_checker(self, start_time, end_time):
        """
        Validates appointment time
        :param start_time: starting time
        :param end_time: ending time
        :return: whether or not the time is valid
        """
        result = [True, "no message"]
        if(start_time < 8 or end_time < 8):
            result[0] = False
            result[1] = "Sorry, no appointments before 8 a.m."
        if (start_time > 18 or end_time > 18):
            result[0] = False
            result[1] = "Sorry, no appointments after 6 p.m."
        return result
