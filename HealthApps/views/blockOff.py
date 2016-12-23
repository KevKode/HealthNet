"""
file: blockOff.py
description: view for blocking off time
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from ..utils import get_user_type
import datetime

from ..models import Appointment, Patient, Doctor, Nurse, Hospital, Hospital_Admin
from ..forms import AppointmentForm, BlockOffForm
from .log_item import CreateLogItem


class CreateBlockOff(CreateView):
    """
    Creates the block off for Doctors
    """
    model = Appointment
    template_name = 'HealthApps/block_off_form.html'
    form_class = BlockOffForm
    success_url = "/calView"

    def get_form_kwargs(self, **kwargs):
        """
        :param kwargs: kwarguments
        :return: kwarguments
        """
        if self.request.user.is_authenticated():
            form_kwargs = super(CreateBlockOff, self).get_form_kwargs(**kwargs)
            form_kwargs["user"] = self.request.user
            return form_kwargs
        else:
            return HttpResponseRedirect('/login')

    def get_context_data(self, **kwargs):
        """
            Sends data to the template
            :param kwargs: kwarguments
            :return:
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
        Validates the block off info
        :param request:
        :param args: arguments
        :param kwargs: kwarguments
        :return:
        """
        # go back to appointment list if hit exit without saving button
        if request.POST.get('goback'):
            return HttpResponseRedirect('/calView')
        else:
            return super(CreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Validates the form
        :param form: form for the user info
        :return:
        """
        appointment = form.save(commit=False)
        a = []

        type_user = get_user_type(self.request.user)

        form.full_clean()  # necessary?
        cleaned_data = form.cleaned_data
        all_apps = Appointment.objects.all()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        weeks = cleaned_data.get("weeks")
        recurring = cleaned_data.get("recurring")
        if type_user == 'doctor':
            appointment.doctor = Doctor.objects.get(user__id=self.request.user.id)
            appointment.patient = None
            end_time = cleaned_data.get("end_time")
        appointment.description = "Doctor " + self.request.user.last_name + " is unavailable. "
        appointment.hospital = Hospital.objects.filter(doctor=Doctor.objects.filter(user=self.request.user))[0]
        if recurring == True:
            newDate = date
            for a in range(weeks):
                newDate = (newDate + datetime.timedelta(days=7))
                a = Appointment(date=newDate, start_time=start_time, end_time=end_time,
                                description=appointment.description, hospital=appointment.hospital,
                                doctor=appointment.doctor, patient=None)
                a.save()
        result = Appointment.conflict_checker(appointment.doctor, appointment.hospital, date, start_time, end_time,
                                              None)

        if not result[0]:
            messages.error(self.request, result[1])
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        CreateLogItem.li_block_off_create(self.request.user, self.object)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UpdateBlockOff(UpdateView):
    """
    Update Block off info
    """
    model = Appointment
    template_name = 'HealthApps/block_off_form.html'
    form_class = BlockOffForm
    success_url = "/calView"

    def get_form_kwargs(self, **kwargs):
        """
        Adds user to kwargs
        :param kwargs: kwarguments
        :return: kwarguments
        """
        form_kwargs = super(UpdateBlockOff, self).get_form_kwargs(**kwargs)
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
            CreateLogItem.li_block_off_cancel(self.request.user, self.object)
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
            date = cleaned_data.get("date")
            start_time = cleaned_data.get("start_time")
            if type_user == 'doctor':
                appointment.doctor = Doctor.objects.get(user__id=self.request.user.id)
                appointment.patient = None
                end_time = cleaned_data.get("end_time")
            newDate = old_appointment.date
            newDate = (newDate + datetime.timedelta(days=7))
            block = Appointment.objects.filter(date=newDate, start_time=old_appointment.start_time, patient=None)
            if len(block) != 0:
                saveDate = date
                while len(block) != 0:
                    saveDate = (saveDate + datetime.timedelta(days=7))
                    block[0].date = saveDate
                    block[0].start_time = start_time
                    block[0].end_time = end_time
                    block[0].save()
                    newDate = newDate
                    newDate = (newDate + datetime.timedelta(days=7))
                    block = Appointment.objects.filter(date=newDate, start_time=old_appointment.start_time,
                                                       patient=None)

            appointment.hospital = Hospital.objects.filter(doctor=Doctor.objects.filter(user=self.request.user))[0]

            result = Appointment.conflict_checker(appointment.doctor, appointment.hospital, date, start_time, end_time,
                                                  old_appointment)
            if not result[0]:
                messages.error(self.request, result[1])
                return self.render_to_response(self.get_context_data(form=form))

            # log that an appointment was updated
            CreateLogItem.li_block_off_edit(self.request.user, self.object, old_appointment)
        return super(UpdateView, self).post(request, *args, **kwargs)


class DeleteBlockOff(DeleteView):
    """
    Deletes the block off
    """
    model = Appointment
    template_name = 'HealthApps/confirm.html'
    success_url = "/calView"

    def get_context_data(self, **kwargs):
        """
        Sends data to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
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

        if request.POST.get('goback'):
            url = '/updateBlockOff/' + str(self.get_object().id)
            # view where user can confirm cancel or go back
            return HttpResponseRedirect(url)
        else:
            # log that an appointment was deleted
            CreateLogItem.li_block_off_cancel(self.request.user, self.object)

            return super(DeleteView, self).post(request, *args, **kwargs)
