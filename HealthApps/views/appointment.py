"""
file: appointment.py
description: view for appointments
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from ..utils import get_user_type
import datetime

from ..models import Appointment, Patient, Doctor, Nurse, Hospital, Hospital_Admin
from ..forms import AppointmentForm
from .log_item import CreateLogItem


def cal_view(request):
    """
    The view for the landing page
    :return: the rendering for the page
    """
    if request.user.is_authenticated():
        user_type = get_user_type(request.user)
        events = []

        if user_type == "doctor":
            appointments = Appointment.objects.filter(doctor__user_id=request.user.id)
        elif user_type == "patient":
            appointments = Appointment.objects.filter(doctor=Patient.objects.filter(user=request.user)[0].doctor)
        elif user_type == "nurse":
            appointments = Appointment.objects.filter(
                doctor__id__in=Doctor.objects.filter(nurse=Nurse.objects.filter(user=request.user)))
        elif user_type == "admin":
            appointments = Appointment.objects.filter(
                hospital=Hospital_Admin.objects.filter(user=request.user)[0].hospital)
        elif request.user.is_superuser:
            appointments = Appointment.objects.all()

        for app in appointments:
            if app.patient is None:
                if user_type == "doctor":
                    events.append({'title': '\nDoctor: ' + app.doctor.user.get_full_name(),
                                   'start': str(datetime.datetime.combine(app.date, app.start_time)),
                                   'end': str(datetime.datetime.combine(app.date, app.end_time))})
                # if a nurse or patient, should be shown us unavailable
                elif user_type == "patient":
                    events.append(
                        {'title': '\nNOT AVAILABLE', 'start': str(datetime.datetime.combine(app.date, app.start_time)),
                         'end': str(datetime.datetime.combine(app.date, app.end_time))})
                elif user_type == "nurse":
                    events.append(
                        {'title': '\nDoctor: ' + app.doctor.user.get_full_name() + '\nNOT AVAILABLE',
                         'start': str(datetime.datetime.combine(app.date, app.start_time)),
                         'end': str(datetime.datetime.combine(app.date, app.end_time))})
            elif user_type == "patient" and request.user.id != app.patient.user.id:
                events.append(
                    {'title': '\nNOT AVAILABLE', 'start': str(datetime.datetime.combine(app.date, app.start_time)),
                     'end': str(datetime.datetime.combine(app.date, app.end_time))})
            else:
                events.append({
                    'title': '\nAppointment\n\n\n\nPatient: ' + app.patient.user.first_name + ' ' + app.patient.user.last_name +
                             '\nDoctor: ' + app.doctor.user.get_full_name() +
                             '\nHospital: ' + app.hospital.__str__() +
                             '\nStart Time: ' + str(app.start_time) +
                             '\nEnd Time: ' + str(app.end_time),
                    'start': str(datetime.datetime.combine(app.date, app.start_time)),
                    'end': str(datetime.datetime.combine(app.date, app.end_time))})

        return render(request, 'HealthApps/cal_view.html',
                      dict(user_type=user_type, events=events))
    else:
        return HttpResponseRedirect('/login')


def app_list(request):
    """
    The view for the appointment list
    :return: rendering for the page
    """
    if request.user.is_authenticated():
        user_type = get_user_type(request.user)

        if user_type == "doctor":
            appointments = Appointment.objects.filter(doctor__user_id=request.user.id)
        elif user_type == "patient":
            appointments = Appointment.objects.filter(patient__user_id=request.user.id)
        elif user_type == "nurse":
            appointments = Appointment.objects.filter(
                doctor__id__in=Doctor.objects.filter(nurse=Nurse.objects.filter(user=request.user)))
        elif user_type == "admin":
            appointments = Appointment.objects.filter(
                hospital=Hospital_Admin.objects.filter(user=request.user)[0].hospital)
        elif request.user.is_superuser:
            appointments = Appointment.objects.all()

        appointments = appointments.order_by('-date', '-start_time')

        return render(request, 'HealthApps/app_list.html', dict(appointments=appointments, user_type=user_type))
    else:
        return HttpResponseRedirect('/login')


class CreateAppointment(CreateView):
    """
    CreateView for the Appointment
    """
    model = Appointment
    template_name = 'HealthApps/appointment_form.html'
    form_class = AppointmentForm
    success_url = "/calView"

    def get_form_kwargs(self, **kwargs):
        """
        :param kwargs: kwarguments
        :return: kwarguments
        """
        if self.request.user.is_authenticated():
            form_kwargs = super(CreateAppointment, self).get_form_kwargs(**kwargs)
            form_kwargs["user"] = self.request.user
            return form_kwargs
        else:
            return HttpResponseRedirect('/login')

    def get_context_data(self, **kwargs):
        """
        :param kwargs: kwarguments
        :return: kwarguments
        """
        if self.request.user.is_authenticated():
            context = super(CreateView, self).get_context_data(**kwargs)

            context['user_type'] = get_user_type(self.request.user)
            context['header'] = 'create'
            return context
        else:
            return HttpResponseRedirect('/login')

    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args: arrguments
        :param kwargs: kwarguments
        :return: Super argument
        """
        # go back to appointment list if hit exit without saving button
        if request.POST.get('goback'):
            return HttpResponseRedirect('/calView')
        else:
            return super(CreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Checks if the form is valid
        :param form: gets the form from the user
        :return: a redirect
        """
        appointment = form.save(commit=False)
        type_user = get_user_type(self.request.user)

        form.full_clean()
        cleaned_data = form.cleaned_data
        all_apps = Appointment.objects.all()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        if (type_user == 'doctor'):
            appointment.doctor = Doctor.objects.get(user__id=self.request.user.id)
            patient = cleaned_data.get("patient")
            end_time = cleaned_data.get("end_time")
        elif (type_user == 'patient'):
            appointment.patient = Patient.objects.get(user__id=self.request.user.id)  # necessary
            appointment.doctor = Patient.objects.get(user__id=self.request.user.id).doctor
            tim = datetime.datetime(100, 1, 1, start_time.hour, start_time.minute, 00)
            end_time = (tim + datetime.timedelta(minutes=30)).time()
            resultTime = Appointment.time_checker(appointment.doctor, start_time.hour, end_time.hour)
            if not resultTime[0]:
                messages.error(self.request, resultTime[1])
                return self.render_to_response(self.get_context_data(form=form))
        elif (type_user == 'nurse'):
            patient = cleaned_data.get("patient")
            appointment.doctor = patient.doctor
            end_time = cleaned_data.get("end_time")

        appointment.hospital = appointment.patient.hospital
        appointment.end_time = end_time  # makes sure end_time is assigned before form is saved

        result = Appointment.conflict_checker(appointment.doctor, appointment.hospital, date, start_time, end_time,
                                              None)

        if not result[0]:
            messages.error(self.request, result[1])
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        CreateLogItem.li_appointment_create(self.request.user, self.object)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UpdateAppointment(UpdateView):
    """
    Updates the appointment
    """
    model = Appointment
    template_name = 'HealthApps/appointment_form.html'
    form_class = AppointmentForm
    success_url = "/calView"

    def get_form_kwargs(self, **kwargs):
        """
        :param kwargs: kwarguments
        :return: kwarguments
        """
        form_kwargs = super(UpdateAppointment, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_context_data(self, **kwargs):
        """
        Sends data to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
        type_user = get_user_type(self.request.user)
        context['user_type'] = type_user
        context['header'] = 'update'
        return context

    def post(self, request, *args, **kwargs):
        """
        Takes and vaidates the info
        :param request:
        :param args: arguments
        :param kwargs: kwarguments
        :return:
        """
        self.object = self.get_object()
        old_appointment = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if request.POST.get('goback'):
            return HttpResponseRedirect('/calView')

        elif request.POST.get('cancel'):
            url = '/cancelAppointment/' + str(self.get_object().id)
            # view where user can confirm cancel or go back
            return HttpResponseRedirect(url)

        # update the appointment, again checking if the date is available
        # if the patient and doctor stay the same, the clean method ignores if the date is unchanged
        # it's the same appointment, so there is no conflict in that special case
        # the doctor is available, because the date that would cause the conflict is the very appointment being updated
        else:
            appointment = form
            type_user = get_user_type(self.request.user)

            form.full_clean()  # necessary?
            cleaned_data = form.cleaned_data
            all_apps = Appointment.objects.all()
            date = cleaned_data.get("date")
            start_time = cleaned_data.get("start_time")
            if (type_user == 'doctor'):
                appointment.doctor = Doctor.objects.get(user__id=self.request.user.id)
                appointment.patient = cleaned_data.get("patient")
                end_time = cleaned_data.get("end_time")
            elif (type_user == 'patient'):
                appointment.patient = Patient.objects.get(user__id=self.request.user.id)  # necessary
                appointment.doctor = Patient.doctor
                tim = datetime.datetime(100, 1, 1, start_time.hour, start_time.minute, 00)
                request.POST['end_time'] = (tim + datetime.timedelta(minutes=30)).time()
                resultTime = Appointment.time_checker(appointment.doctor, start_time.hour,
                                                      request.POST['end_time'].hour)
                if not resultTime[0]:
                    messages.error(self.request, resultTime[1])
                    return self.render_to_response(self.get_context_data(form=form))
                end_time = (tim + datetime.timedelta(minutes=30)).time()
            elif (type_user == 'nurse'):
                appointment.patient = cleaned_data.get("patient")
                appointment.doctor = appointment.patient.doctor
                end_time = cleaned_data.get("end_time")

            appointment.hospital = appointment.patient.hospital

            result = Appointment.conflict_checker(appointment.doctor, appointment.hospital, date, start_time, end_time,
                                                  old_appointment)
            if not result[0]:
                messages.error(self.request, result[1])
                return self.render_to_response(self.get_context_data(form=form))

            # log that an appointment was updated
            CreateLogItem.li_appointment_edit(self.request.user, self.object, old_appointment)
        return super(UpdateView, self).post(request, *args, **kwargs)


class DeleteAppointment(DeleteView):
    """
    Deletes the Appointment
    """
    model = Appointment
    template_name = 'HealthApps/confirm.html'
    success_url = "/calView"

    def get_context_data(self, **kwargs):
        """
        Sends info to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        """
        Validates info
        :param request:
        :param args: arrguments
        :param kwargs: kwarguments
        :return:
        """
        self.object = self.get_object()

        if request.POST.get('goback'):
            url = '/updateAppointment/' + str(self.get_object().id)
            # view where user can confirm cancel or go back
            return HttpResponseRedirect(url)
        else:
            # log that an appointment was deleted

            if (self.object.patient != None):
                CreateLogItem.li_appointment_cancel(self.request.user, self.object)

            return super(DeleteView, self).post(request, *args, **kwargs)
