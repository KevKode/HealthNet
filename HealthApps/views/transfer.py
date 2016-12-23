"""
file: transfer.py
description: handles transfer views
"""

from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, CreateView
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from datetime import datetime
from django.contrib import messages
from ..utils import get_user_type
from ..models import Patient, Doctor, Nurse, Hospital_Admin, Hospital, Prescription, Test
from ..views import CreateLogItem, CreateEMREntry
from ..forms import ProfileForm, UserInfoForm, PrescriptionForm, TestForm, TransferForm


def transfer_patient_list(request):
    """
    View for the transfe patient list
    :param request:
    :return: rendering for page
    """
    user_type = get_user_type(request.user)

    if user_type == "doctor":
        doctor = Doctor.objects.filter(user=request.user)[0]
        hospitals = Hospital.objects.filter(doctor=doctor)
        patients = Patient.objects.filter(transfer_to__in=hospitals) | Patient.objects.filter(admitted_to__in=hospitals)
        patients = patients.order_by('user__last_name')
    elif user_type == "admin":
        h_a = Hospital_Admin.objects.filter(user=request.user)[0]
        hospital = Hospital.objects.filter(hospital_admin=h_a)
        patients = Patient.objects.filter(transfer_to=hospital) | Patient.objects.filter(admitted_to=hospital)
        patients = patients.order_by('user__last_name')

    return render(request, 'HealthApps/transfer_patient_list.html', dict(patients=patients, user_type=user_type))


class UpdateTransfer(UpdateView):
    """
    Updates the patient's transfer items
    """
    model = Patient
    form_class = TransferForm
    template_name = 'HealthApps/transfer_form.html'
    success_url = '/transferPatientList'

    def get_form_kwargs(self, **kwargs):
        """
        :param kwargs: kwarguments
        :return: kwarguments
        """
        form_kwargs = super(UpdateTransfer, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_context_data(self, **kwargs):
        """
        Sends data to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
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
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        patient = self.object
        old_hospital = patient.admitted_to

        if request.POST.get('goback'):
            return HttpResponseRedirect('/transferPatientList')
        else:
            form.full_clean()
            cleaned_data = form.cleaned_data
            transfer_to = cleaned_data.get("transfer_to")
            patient = self.object

            new_hospital = transfer_to
            if transfer_to is not None:
                request.POST['admitted_to'] = None

            CreateLogItem.li_transfer(patient, old_hospital, new_hospital)

            CreateEMREntry.emr_transfer(patient, old_hospital, new_hospital)

        return super(UpdateView, self).post(request, *args, **kwargs)


def admit_patient(request, pk):
    """
    View for admit patient
    :param request:
    :param pk: patient primary key
    :return: redirect
    """
    patient = Patient.objects.get(pk=pk)

    if patient.admitted_to is None and patient.transfer_to is None:
        patient.admitted_to = patient.hospital
    elif patient.admitted_to is None and patient.transfer_to is not None:
        patient.admitted_to = patient.transfer_to

    patient.transfer_to = None
    patient.save()

    CreateEMREntry.emr_admit(patient, patient.admitted_to)

    CreateLogItem.li_admit(patient, patient.admitted_to)

    return HttpResponseRedirect("/EMR/" + str(patient.id), dict(user_type=get_user_type(request.user)))


def discharge_patient(request, pk):
    """
    View for discharge patient
    :param request:
    :param pk: patient primary key
    :return: redirect
    """
    patient = Patient.objects.get(pk=pk)
    hospital = patient.admitted_to
    patient.admitted_to = None
    patient.save()

    CreateEMREntry.emr_discharge(patient, hospital)

    CreateLogItem.li_discharge(patient, hospital)

    return HttpResponseRedirect("/transferPatientList", dict(user_type=get_user_type(request.user)))