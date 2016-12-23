"""
file: statistics.py
description: views and functions for statistics
"""

from django.shortcuts import render
from ..utils import get_user_type
import datetime
from django.contrib import messages

from django.db.models import Count
from ..models import Appointment, Patient, Doctor, Nurse, Hospital_Admin, Prescription
from ..forms import StatisticsForm


def number_joined(elements, start_date, end_date):
    """
    Calculates stats joined
    :param elements: stat elements
    :param start_date: the starting date for stats
    :param end_date: the ending date for stats
    :return: the joined stats
    """
    joined = 0
    for person in elements:
        date_joined = person.user.date_joined
        date_joined = date_joined - datetime.timedelta(hours=5)
        if end_date >= date_joined.date() >= start_date:
            joined += 1
    return str(joined)


def avg_app_duration(all_apps):
    """
    Calculates average appointment duration
    :param all_apps: all appointments
    :return: average
    """
    total_dur = datetime.timedelta()
    total_apps = 0
    for app in all_apps:
        duration = datetime.datetime.combine(datetime.date.min, app.end_time) - datetime.datetime.combine(
            datetime.date.min, app.start_time)
        total_dur += duration
        total_apps += 1
    if total_apps == 0:
        return total_dur
    else:
        return total_dur / total_apps


def form_handle(request):
    """
    View for statistics
    :param request: POST request
    :return: rendered template
    """
    form = StatisticsForm()
    info = []
    if request.method == 'POST':
        form = StatisticsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            start_date = cd.get('start_date')
            end_date = cd.get('end_date')
            if start_date > end_date:
                messages.error(request, 'The end date cannot occur before the start date.')
                return render(request, 'HealthApps/statistics.html',
                              dict(form=form, user_type=get_user_type(request.user), info=info))
            info.append("General System Statistics:")
            if get_user_type(request.user) == 'doctor':
                doctor = Doctor.objects.filter(user=request.user)
                apps_in_range = Appointment.objects.filter(date__range=(start_date, end_date), doctor=doctor).exclude(
                    patient=None)
                info.append("Total number of patients: " +
                            str(Patient.objects.filter(doctor=doctor).count()))
                info.append("Total number of appointments: " +
                            str(Appointment.objects.filter(doctor=doctor).exclude(patient=None).count()))
                info.append("Total number of upcoming appointments: " +
                            str(Appointment.objects.filter(doctor=doctor,
                                                           date__gte=datetime.date.today()).exclude(
                                patient=None).count()))
                patients = Patient.objects.filter(doctor=doctor)
                if patients:
                    info.append("Average number of appointments per patient: " +
                                str(Appointment.objects.filter(
                                    doctor=doctor).exclude(patient=None).count() / Patient.objects.filter(
                                    doctor=doctor).count()))
                apps_reason = Appointment.objects.filter(doctor=doctor).exclude(patient=None).exclude(
                    description=None).values_list('description').annotate(reason=Count('description')).order_by(
                    '-reason')
                if apps_reason:
                    info.append("Most common reason for an appointment: " + apps_reason[0][0])
                prescription_names = Prescription.objects.filter(doctor=doctor).values_list('name').annotate(
                    name_count=Count('name')).order_by('-name_count')
                if prescription_names:
                    info.append("Most common prescription: " + prescription_names[0][0])

                info.append("Statistics for the time period between " + start_date.strftime(
                    '%m/%d/%Y') + " and " + end_date.strftime('%m/%d/%Y') + ":")
                info.append("Number of patients joined: " +
                            number_joined(Patient.objects.filter(doctor=doctor), start_date, end_date))
                info.append("Number of appointments scheduled: " + str(apps_in_range.count()))
                if patients:
                    info.append("Average number of appointments per patient: " +
                                str(apps_in_range.count() / Patient.objects.filter(doctor=doctor).count()))
                info.append("Average length of an appointment: " + str(avg_app_duration(apps_in_range)))

            elif get_user_type(request.user) == 'admin':
                hospital = Hospital_Admin.objects.filter(user=request.user)[0].hospital
                patients = Patient.objects.filter(hospital=hospital)
                info.append("Total number of doctors: " +
                            str(Doctor.objects.filter(hospitals=hospital).count()))
                info.append("Total number of nurses: " +
                            str(Nurse.objects.filter(hospitals=hospital).count()))
                info.append("Total number of patients: " +
                            str(Patient.objects.filter(hospital=hospital).count()))
                info.append("Total number of appointments: " +
                            str(Appointment.objects.filter(hospital=hospital).exclude(patient=None).count()))
                info.append("Total number of upcoming appointments: " +
                            str(Appointment.objects.filter(hospital=hospital,
                                                           date__gte=datetime.date.today()).exclude(
                                patient=None).count()))
                docs = Appointment.objects.filter(hospital=hospital).exclude(patient=None).values_list(
                    'doctor').annotate(doc=Count('doctor')).order_by('-doc')
                if docs:
                    info.append("Doctor with the most appointments: " +
                                str(Doctor.objects.get(pk=docs[0][0])) + ' with ' + str(docs[0][1]) + ' appointments')
                if patients:
                    info.append("Average number of appointments per patient: " +
                                str(Appointment.objects.filter(date__gte=datetime.date.today(),
                                                               hospital=hospital).exclude(
                                    patient=None).count() / patients.count()))
                apps_reason = Appointment.objects.filter(hospital=hospital).exclude(patient=None).exclude(
                    description=None).values_list('description').annotate(reason=Count('description')).order_by(
                    '-reason')
                if apps_reason:
                    info.append("Most common reason for an appointment: " + apps_reason[0][0])
                prescription_names = Prescription.objects.filter(patient__in=patients).values_list('name').annotate(
                    name_count=Count('name')).order_by('-name_count')
                if prescription_names:
                    info.append("Most common prescription: " + prescription_names[0][0])

                info.append("Statistics for the time period between " + start_date.strftime(
                    '%m/%d/%Y') + " and " + end_date.strftime('%m/%d/%Y') + ":")
                info.append("Number of doctors joined: " +
                            number_joined(Doctor.objects.filter(hospitals=hospital), start_date, end_date))
                info.append("Number of nurses joined: " +
                            number_joined(Nurse.objects.filter(hospitals=hospital), start_date, end_date))
                info.append("Number of patients joined: " +
                            number_joined(Patient.objects.filter(hospital=hospital), start_date, end_date))
                apps_in_range = Appointment.objects.filter(date__range=(start_date, end_date),
                                                           hospital=hospital).exclude(patient=None)
                info.append("Number of appointments scheduled: " + str(apps_in_range.count()))
                if patients:
                    info.append("Average number of appointments per patient: " + str(
                        apps_in_range.count() / patients.count()))
                info.append("Average length of an appointment: " + str(avg_app_duration(apps_in_range)))

    return render(request, 'HealthApps/statistics.html',
                  dict(form=form, user_type=get_user_type(request.user), info=info))
