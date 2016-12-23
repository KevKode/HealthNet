"""
file: profile.py
description: views for profile
"""

from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, CreateView
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from datetime import datetime

from ..utils import get_user_type
from ..models import Patient, Doctor, Nurse, Hospital_Admin, Prescription, Test, EMR_Entry, Hospital
from ..views import CreateLogItem, CreateEMREntry
from ..forms import ProfileForm, UserInfoForm, PrescriptionForm, TestForm, EMRForm, UserForm


def patient_list(request):
    """
    View for patient list
    :param request: request to get user and user type
    :return: rendered template
    """
    user_type = get_user_type(request.user)

    if user_type == "doctor":
        doctor = Doctor.objects.filter(user=request.user)[0]
        patients = Patient.objects.filter(doctor=doctor)
        patients = patients.order_by('user__last_name')
    elif user_type == "nurse":
        patients = Patient.objects.filter(
            doctor__in=Doctor.objects.filter(nurse=Nurse.objects.filter(user=request.user)[0])).order_by(
            'user__last_name')
    elif user_type == "admin":
        h_a = Hospital_Admin.objects.filter(user=request.user)[0]
        hospital = Hospital.objects.filter(hospital_admin=h_a)
        patients = Patient.objects.filter(hospital=hospital).order_by('user__last_name')

    return render(request, 'HealthApps/patient_list.html', dict(patients=patients, user_type=user_type))


def profile(request):
    """
    View for patient profile
    :param request: to get user and user type
    :return: rendered template
    """
    print("User type:", get_user_type(request.user))
    if request.user.is_superuser or Doctor.objects.filter(
            user__username=request.user.username).exists() or Nurse.objects.filter(
        user__username=request.user.username).exists() or Hospital_Admin.objects.filter(
        user__username=request.user.username).exists():
        return HttpResponseRedirect('notImplemented')
    elif not Patient.objects.filter(user__username=request.user.username).exists():
        return HttpResponseRedirect('/createPatient')
    else:
        patient = Patient.objects.get(user__username=request.user.username)

    return render(request, 'HealthApps/profile.html', dict(patient=patient, user_type=get_user_type(request.user)))


class UpdateProfile(UpdateView):
    """
    View for updating profile
    """
    model = Patient
    form_class = ProfileForm
    template_name = 'HealthApps/patient_profile.html'
    success_url = '/profile'

    def get_context_data(self, **kwargs):
        """
        Adds user type to kwargs
        :param kwargs: kwarguments
        :return: context
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def user_matches_patient(self, request, **kwargs):
        """
        Returns whether user belongs to patient
        :param request: to get user
        :param kwargs: kwarguments
        :return: whether or not user belongs to patient
        """
        if request.user.is_authenticated():
            patient = Patient.objects.get(pk=kwargs['pk'])
            return patient.user.id == request.user.id
        return False

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects to login page if user doesn't match patient
        :param request: to get user
        :param args: arguments
        :param kwargs: kwarguments
        :return: dispatch
        """
        if not self.user_matches_patient(request, **kwargs):
            return HttpResponseRedirect('/login')
        return super(UpdateProfile, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Creates log item and redirects
        :param form: validated form
        :return: redirect
        """
        old_patient = self.request.user.patient
        self.object = form.save()

        CreateLogItem.li_patient_edit(self.object, old_patient)

        return HttpResponseRedirect(self.success_url)


class UpdateUser(UpdateView):
    """
    View for updating user
    """
    model = User
    template_name = 'HealthApps/user_profile.html'
    form_class = UserForm
    success_url = "/profile"

    def get_form_kwargs(self, **kwargs):
        """
        Adds user to kwargs
        :param kwargs: kwarguments
        :return: kwargs
        """
        form_kwargs = super(UpdateUser, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs

    def get_context_data(self, **kwargs):
        """
        Adds user type and header to context
        :param kwargs: kwarguments
        :return: context
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
        type_user = get_user_type(self.request.user)
        context['user_type'] = type_user
        context['header'] = 'update'
        return context