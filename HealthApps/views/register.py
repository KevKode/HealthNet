"""
file: register.py
description: handles views and functions for registration
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView

from ..utils import get_user_type
from ..forms import PatientForm, DoctorForm, NurseForm, HospitalAdminForm
from ..models import Patient, Doctor, Nurse, Hospital_Admin
from .log_item import CreateLogItem

def registration_options(request):
    """
    View for registration options
    :param request: used to determine user type
    :return: the rendered registration options template
    """
    return render(request, 'HealthApps/registration_options.html', dict(user_type=get_user_type(request.user)))


class CreateDoctor(CreateView):
    """
    View for Doctor Registration
    """
    template_name = 'HealthApps/register_doctor.html'
    model = Doctor
    form_class = DoctorForm
    success_url = '/index.html'

    def get_form_kwargs(self):
        """
        Updates form kwargs to include the request's user
        :return: updated kwargs
        """
        kwargs = super(CreateDoctor, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class CreatePatient(CreateView):
    """
    View for Patient Registration
    """
    form_class = PatientForm
    model = Patient
    template_name = 'HealthApps/register_patient.html'
    success_url = 'login'


class CreateNurse(CreateView):
    """
    View for Nurse Registration
    """
    form_class = NurseForm
    model = Nurse
    template_name = 'HealthApps/register_nurse.html'
    success_url = '/index.html'

    def get_form_kwargs(self):
        """
        Updates form kwargs to include the request's user
        :return: updated kwargs
        """
        kwargs = super(CreateNurse, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class CreateHospitalAdmin(CreateView):
    """
    View for Hospital Admin Registration
    """
    form_class = HospitalAdminForm
    model = Hospital_Admin
    template_name = 'HealthApps/register_admin.html'
    success_url = '/index.html'


def staffView(request):
    """
    View for staff approval list
    :param request: used to determine user type
    :return: the rendered staff approval list template
    """
    doctors = []
    dHosp = ''
    nurses = []
    nHosp =''
    for d in Doctor.objects.all():
        if not d.user.is_active:
            doctors.append(d)
            for h in d.hospitals.all():
                if dHosp == '':
                    dHosp += h.name
                else:
                    dHosp += ', '+h.name
    for n in Nurse.objects.all():
        if not n.user.is_active:
            nurses.append(n)
            for h in n.hospitals.all():
                if nHosp == '':
                    nHosp += h.name
                else:
                    nHosp += ', '+h.name
    user_type = get_user_type(request.user)
    return render(request, 'HealthApps/approve_list.html',
                  dict(user_type=user_type, doctors=doctors, nurses=nurses, dHosp=dHosp, nHosp=nHosp))


def approve_doc(request, pk):
    """
    Approves (enables) specified doctor
    :param request: currently unused
    :param pk: the primary key of the doctor
    :return: redirect to staff approval list
    """
    doc = Doctor.objects.get(pk=pk)
    doc.user.is_active = True
    doc.user.save()

    CreateLogItem.li_doctor_approve(doc)

    return HttpResponseRedirect("/approveList")


def approve_nur(request, pk):
    """
    Approves (enables) specified nurse
    :param request: currently unused
    :param pk: the primary key of the nurse
    :return: redirect to staff approval list
    """
    nur = Nurse.objects.get(pk=pk)
    nur.user.is_active = True
    nur.user.save()

    CreateLogItem.li_nurse_approve(nur)

    return HttpResponseRedirect("/approveList")