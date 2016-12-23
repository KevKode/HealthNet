"""
file: urls.py
description: urls with regex patterns for healthnet
"""

from django.conf.urls import url
from django.contrib.auth import views
from django.contrib.auth import views as auth_views

from .views.transfer import UpdateTransfer
from .views.blockOff import CreateBlockOff, UpdateBlockOff
from .views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^createPatient', CreatePatient.as_view(), name='createPatient'),
    url(r'^index.html$', index, name='index'),
    # can view all of the appointments
    url(r'^appList$', app_list, name='appList'),
    # can create new appointment here
    url(r'^createAppointment$', CreateAppointment.as_view(), name='createAppointment'),
    # can update appointment with given id number
    url(r'^updateAppointment/(?P<pk>[0-9]+)/$', UpdateAppointment.as_view(), name='updateAppointment'),
    url(r'^cancelAppointment/(?P<pk>[0-9]+)/$', DeleteAppointment.as_view(), name='cancelAppointment'),
    # user auth urls
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^calView$', cal_view, name='calView'),

    url(r'^logTable', log_table, name='logTable'),
    url(r'^logItem/(?P<pk>[0-9]+)/$', view_log_item, name='logItem'),
    url(r'^patientList$', patient_list, name='patientList'),
    url(r'^transferPatientList$', transfer_patient_list, name='transferPatientList'),
    url(r'^createPrescription/(?P<pk>[0-9]+)/$', CreatePrescription.as_view(), name='createPrescription'),
    url(r'^createTest/(?P<pk>[0-9]+)/$', CreateTest.as_view(), name='createTest'),
    url(r'^createCustomEntry/(?P<pk>[0-9]+)/$', CreateCustomEntry.as_view(), name='createEMREntry'),
    url(r'^editVitals/(?P<pk>[0-9]+)/$', UpdateVitals.as_view(), name='editVitals'),
    url(r'^getPrescription/(?P<pk>[0-9]+)/$', get_prescription, name='getPrescription'),
    url(r'^getTest/(?P<pk>[0-9]+)/$', get_test, name='getTest'),

    url(r'^EMR/(?P<pk>[0-9]+)/$', emr, name='emr'),
    url(r'^toEMR/(?P<pk>[0-9]+)/$', to_emr, name='toEMR'),
    url(r'^emrEntry/(?P<pk>[0-9]+)$', emr_entry, name='emrEntry'),

    url(r'^delete/(?P<pk>[0-9]+)/$', delete_prescription, name='deletePrescription'),
    url(r'^release/(?P<pk>[0-9]+)/$', release_test, name='releaseResult'),
    url(r'^approveDoc/(?P<pk>[0-9]+)/$', approve_doc, name='approveDoc'),
    url(r'^approveNur/(?P<pk>[0-9]+)/$', approve_nur, name='approveNur'),
    url(r'^hide/(?P<pk>[0-9]+)/$', hide_entry, name='hideEntry'),
    url(r'^show/(?P<pk>[0-9]+)/$', show_entry, name='showEntry'),
    url(r'^admit/(?P<pk>[0-9]+)/$', admit_patient, name='admit'),
    url(r'^discharge/(?P<pk>[0-9]+)/$', discharge_patient, name='discharge'),
    url(r'^exportVitalsEntries/(?P<pk>[0-9]+)/$', export_vitals_entries, name='discharge'),

    url(r'^statistics$', form_handle, name='statistics'),

    url(r'^profile', profile, name='profile'),
    url(r'^updateProfile/(?P<pk>\d+)/', UpdateProfile.as_view(), name='updateProfile'),
    url(r'^updateUser/(?P<pk>[0-9]+)/$', UpdateUser.as_view(), name='updateUser'),
    url(r'^createHospital', CreateHospital.as_view(), name='createHospital'),
    url(r'^createDoctor', CreateDoctor.as_view(), name='createDoctor'),
    url(r'^createNurse', CreateNurse.as_view(), name='createNurse'),
    url(r'^createAdmin', CreateHospitalAdmin.as_view(), name='createAdmin'),
    url(r'^registerOptions$', registration_options, name='registerOptions'),
    url(r'^blockOff$', CreateBlockOff.as_view(), name='blockOff'),
    url(r'^updateBlockOff/(?P<pk>[0-9]+)/$', UpdateBlockOff.as_view(), name='updateTransfer'),
    url(r'^updateTransfer/(?P<pk>[0-9]+)/$', UpdateTransfer.as_view(), name='updateTransfer'),
    url(r'^approveList$', staffView, name='approveStaff'),
    url(r'^cascade_select/hospital-to-doctor/$', hospital_to_doctor, name='hospitalToDoctor'),
    url(r'^handleCSV$', handle_csv, name='handleCSV'),
    url(r'^exportCSV/(?P<string>[\w\-\.]+)/$', export_csv, name='exportCSV'),
    url(r'^importCSV/(?P<string>[\w\-\.]+)/$', import_csv, name='importCSV'),
]
