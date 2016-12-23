"""
file: tests.py
description: tests for system
"""

from django.test import TestCase
from django.contrib.auth.models import User
from .models import *
import datetime


# Create your tests here.

class AppointmentTests(TestCase):
    """
    Tests for appointments
    """
    def setUp(self):
        """
        Sets up initial objects for test
        :return:
        """
        bhh = Hospital.objects.create(name='Beacon Hills Hospital')
        dph = Hospital.objects.create(name='Devenford Prep Hospital')
        deaton = User.objects.create_user('Alan Deaton', 'd@d.com')
        scott = User.objects.create_user('Scott McCall', 'm@m.com')
        derek = User.objects.create_user('Derek Hale', 'h@h.com')
        jen = User.objects.create_user('Jennifer', 'j@j.com')
        doc_deaton = Doctor.objects.create(user=deaton, max_patients=2)
        # nurse_jen = Nurse.objects.create(user=jen, hospitals=bhh)
        pat_scott = Patient.objects.create(user=scott, hospital=bhh, doctor=doc_deaton)
        pat_derek = Patient.objects.create(user=derek, hospital=bhh, doctor=doc_deaton)
        doc_deaton.patients = [pat_scott, pat_derek]
        doc_deaton.hospitals = [bhh]
        # nurse_jen.doctors = doc_deaton

    def test_app_where_doctor_is_available(self):
        """
        Asserts availability
        :return:
        """
        bhh = Hospital.objects.get(name='Beacon Hills Hospital')
        pat_derek = Patient.objects.get(user=User.objects.get(username='Derek Hale'))
        doc_deaton = Doctor.objects.get(user=User.objects.get(username='Alan Deaton'))
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(13)
        end_time = datetime.time(14)
        doctor = doc_deaton
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], True)

    def test_app_with_same_start_time(self):
        """
        Asserts can't make appointments at same time
        :return:
        """
        bhh = Hospital.objects.get(name='Beacon Hills Hospital')
        pat_derek = Patient.objects.get(user=User.objects.get(username='Derek Hale'))
        doc_deaton = Doctor.objects.get(user=User.objects.get(username='Alan Deaton'))
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(13)
        end_time = datetime.time(14)
        Appointment.objects.create(date=date, start_time=start_time, end_time=end_time, hospital=bhh,
                                   doctor=doc_deaton, patient=pat_derek)
        doctor = doc_deaton
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Sorry, another appointment starts at that time. Please try again.")

    def test_app_set_in_the_past(self):
        """
        Asserts appointments must be in present / future
        :return:
        """
        bhh = Hospital.objects.get(name='Beacon Hills Hospital')
        doc_deaton = Doctor.objects.get(user=User.objects.get(username='Alan Deaton'))
        doctor = doc_deaton
        date = datetime.date(2015, 12, 1)
        start_time = datetime.time(13)
        end_time = datetime.time(14)
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Sorry, you cannot create appointments set in the past. Please try again.")

    def test_app_is_less_than_thirty_minutes(self):
        """
        Asserts appointments must not be less than thirty minutes
        :return:
        """
        bhh = Hospital.objects.get(name='Beacon Hills Hospital')
        doc_deaton = Doctor.objects.get(user=User.objects.get(username='Alan Deaton'))
        doctor = doc_deaton
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(13)
        end_time = datetime.time(13, 29)
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Sorry, you cannot create appointments less than thirty minutes. Please try again.")

    def test_ten_min_between_apps(self):
        """
        Asserts that there must be a ten minute gap between appointments
        :return:
        """
        bhh = Hospital.objects.get(name='Beacon Hills Hospital')
        pat_derek = Patient.objects.get(user=User.objects.get(username='Derek Hale'))
        doc_deaton = Doctor.objects.get(user=User.objects.get(username='Alan Deaton'))
        doctor = doc_deaton
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(13)
        end_time = datetime.time(14)
        Appointment.objects.create(date=date, start_time=start_time, end_time=end_time, hospital=bhh,
                                   doctor=doc_deaton, patient=pat_derek)
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(14, 9)
        end_time = datetime.time(14, 39)
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1],
                         "Sorry, the appointment starts too soon to the end of another appointment. Please try again.")
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(12, 21)
        end_time = datetime.time(12, 51)
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1],
                         "Sorry, the appointment ends too soon to the start of another appointment. Please try again.")

    def test_first_app_sets_hospital(self):
        """
        Asserts that appointments and doctors properly correspond to hospitals
        :return:
        """
        bhh = Hospital.objects.get(name='Beacon Hills Hospital')
        dph = Hospital.objects.get(name='Devenford Prep Hospital')
        pat_derek = Patient.objects.get(user=User.objects.get(username='Derek Hale'))
        doc_deaton = Doctor.objects.get(user=User.objects.get(username='Alan Deaton'))
        doctor = doc_deaton
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(13)
        end_time = datetime.time(14)
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], True)
        Appointment.objects.create(date=date, start_time=start_time, end_time=end_time, hospital=bhh,
                                   doctor=doc_deaton, patient=pat_derek)
        date = datetime.date(2016, 12, 30)
        start_time = datetime.time(14, 10)
        end_time = datetime.time(14, 40)
        result = Appointment.conflict_checker(doctor, dph, date, start_time, end_time, None)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "Sorry, the doctor is in a different hospital on that date. Please try again.")
        result = Appointment.conflict_checker(doctor, bhh, date, start_time, end_time, None)
        self.assertEqual(result[0], True)
