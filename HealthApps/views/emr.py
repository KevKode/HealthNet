"""
file: emr.py
description: views for electronic medical records
"""

from django.http import HttpResponseRedirect
from ..models import EMR_Entry, Patient, Prescription, Test, Doctor, Appointment, Hospital, Hospital_Admin
from ..forms import EMRForm, PrescriptionForm, TestForm, VitalsForm
from django.views.generic import CreateView, UpdateView
from django.shortcuts import render
from datetime import datetime
from ..utils import get_user_type
from django.contrib.auth.models import User
from .log_item import CreateLogItem
from django.core.files import File


def export_vitals_entries(request, pk):
    """
    Exports vitals to txt
    :param request: request object to get user type
    :param pk: private key
    :return: redirect
    """
    patient = Patient.objects.get(pk=pk)
    emr = EMR_Entry.objects.filter(patient__id=pk, shown=True)

    f = open('vitals_and_entries.txt', 'w')
    file = File(f)
    string = ""

    string += "Vitals: \n"
    if patient.height:
        string += " - Height: " + str(patient.height) + "\n"
    else:
        string += " - Height: None\n"

    if patient.weight:
        string += " - Weight: " + str(patient.weight) + "\n"
    else:
        string += " - Weight: None\n"

    if patient.cholesterol:
        string += " - Cholesterol: " + patient.cholesterol + "\n"
    else:
        string += " - Cholesterol: None\n"

    if patient.pulse:
        string += " - Pulse: " + str(patient.pulse) + "\n"
    else:
        string += " - Pulse: None\n"

    if patient.temperature:
        string += " - Temperature: " + str(patient.temperature) + "\n"
    else:
        string += " - Temperature: None\n"

    if patient.blood_pressure:
        string += " - Blood Pressure: " + patient.blood_pressure + "\n"
    else:
        string += " - Blood Pressure: None\n"

    if patient.blood_type:
        string += " - Blood Type: " + patient.blood_type + "\n"
    else:
        string += " - Blood Type: None\n"

    string += "\nEMR Entries:\n\n"

    for entry in emr:
        string += " Type: " + entry.type + "\n"
        string += "  - Timestamp: " + entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") + "\n"

        if entry.type == "Test Create" or entry.type == "Test Release":
            string += "  - Hospital: " + entry.test.hospital.name + "\n"
            string += "  - Doctor: " + entry.test.doctor.user.first_name + " " + entry.test.doctor.user.last_name + "\n"
            string += "  - Name: " + entry.test.name + "\n"
            string += "  - Description: " + entry.test.description + "\n"
            if entry.test.file.name:
                string += "  - File: " + entry.test.file.url + "\n"

        elif entry.type == "Prescribe Prescription" or entry.type == "Delete Prescription":
            string += "  - Doctor: " + entry.prescription.doctor.user.first_name + " " + entry.prescription.doctor.user.last_name + "\n"
            string += "  - Name: " + entry.prescription.name + "\n"
            string += "  - Dosage Amount: " + str(entry.prescription.dosage_amount) + " " + entry.prescription.dosage_unit + "\n"
            string += "  - Dosage Frequency: " + str(entry.prescription.frequency_amount) + " doses " + entry.prescription.frequency_unit + "\n"

        else:
            string += "  - Description: " + entry.description + "\n"

        string += "\n"

    file.write(string)
    file.close()
    f.close()

    return HttpResponseRedirect("/EMR/" + str(patient.id), dict(user_type=get_user_type(request.user)))


def hide_entry(request, pk):
    """
    Hides entry
    :param request:
    :param pk: primary key for the entry
    :return:
    """
    entry = EMR_Entry.objects.get(pk=pk)
    entry.shown = False
    entry.save()

    return HttpResponseRedirect("/EMR/" + str(entry.patient.id), dict(user_type=get_user_type(request.user)))


def show_entry(request, pk):
    """
    Shows entry
    :param request:
    :param pk: primary key for the entry
    :return:
    """
    entry = EMR_Entry.objects.get(pk=pk)
    entry.shown = True
    entry.save()

    return HttpResponseRedirect("/EMR/" + str(entry.patient.id), dict(user_type=get_user_type(request.user)))


def release_test(request, pk):
    """
    Releases entry
    :param request:
    :param pk: primary key for the entry
    :return:
    """
    test = Test.objects.get(pk=pk)
    test.released = True
    test.save()

    CreateLogItem.li_test_release(test)

    CreateEMREntry.emr_test_release(test)

    return HttpResponseRedirect("/EMR/" + str(test.patient.id), dict(user_type=get_user_type(request.user)))


def delete_prescription(request, pk):
    """
    Deletes entry
    :param request:
    :param pk: primary key for the entry
    :return:
    """
    prescription = Prescription.objects.get(pk=pk)
    prescription.prescribed = False
    prescription.save()

    CreateLogItem.li_prescription_delete(prescription)

    CreateEMREntry.emr_prescription_delete(prescription)

    return HttpResponseRedirect("/EMR/" + str(prescription.patient.id), dict(user_type=get_user_type(request.user)))


class UpdateVitals(UpdateView):
    """
    Updates the patient's vitals
    """
    model = Patient
    form_class = VitalsForm
    template_name = "HealthApps/vitals_form.html"

    def get_context_data(self, **kwargs):
        """
        Sends data to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def form_valid(self, form):
        """
        Validates the form
        :param form: info from the form
        :return:
        """
        patient = form.save(commit=False)
        patient.save()

        CreateLogItem.li_vitals_edit(patient)

        CreateEMREntry.emr_vitals_edit(patient)

        return HttpResponseRedirect("/EMR/" + str(patient.id))


class CreateCustomEntry(CreateView):
    """
    Creates Custom entry
    """
    model = EMR_Entry
    form_class = EMRForm
    template_name = 'HealthApps/emr_form.html'

    def get_context_data(self, **kwargs):
        """
        Sends data to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(CreateView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def form_valid(self, form):
        """
        Validates the form
        :param form: info from the form
        :return:
        """
        emr_entry = form.save(commit=False)
        emr_entry.type = "[Custom] " + emr_entry.type
        emr_entry.timestamp = datetime.now()
        emr_entry.patient = Patient.objects.get(id=self.kwargs['pk'])

        emr_entry.save()

        CreateLogItem.li_custom_entry_create(self.request.user, emr_entry)

        return HttpResponseRedirect("/EMR/" + str(emr_entry.patient.id))


class CreateTest(CreateView):
    """
    Creates a test
    """
    model = Test
    form_class = TestForm
    template_name = 'HealthApps/test_form.html'

    def get_context_data(self, **kwargs):
        """
        Sends data to the template
        :param kwargs: kwarguments
        :return:
        """
        context = super(CreateView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def form_valid(self, form):
        """
        Validates the form
        :param form: info from the form
        :return:
        """
        test = form.save(commit=False)
        test.timestamp = datetime.now()
        test.doctor = Doctor.objects.get(user_id=self.request.user.id)
        test.patient = Patient.objects.get(id=self.kwargs['pk'])
        test.hospital = Patient.objects.get(id=self.kwargs['pk']).hospital
        array = test.file.name.split('/')
        test.filename = array[len(array) - 1]

        test.save()

        CreateLogItem.li_test_create(test)

        CreateEMREntry.emr_test_create(test)

        return HttpResponseRedirect("/EMR/" + str(test.patient.id))


class CreatePrescription(CreateView):
    """
    Create Prescription
    """
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'HealthApps/prescription_form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def form_valid(self, form):
        """
        Validates the form
        :param form: info from the form
        :return:
        """
        prescription = form.save(commit=False)
        prescription.timestamp = datetime.now()
        prescription.doctor = Doctor.objects.get(user_id=self.request.user.id)
        prescription.patient = Patient.objects.get(id=self.kwargs['pk'])

        prescription.save()

        CreateLogItem.li_prescription_create(prescription)

        CreateEMREntry.emr_prescription_create(prescription)

        return HttpResponseRedirect("/EMR/" + str(prescription.patient.id))


def to_emr(request, pk):
    """
    Sends items to EMR
    :param request:
    :param pk: primary key for emr
    :return: redirect
    """
    patient = Patient.objects.get(user=User.objects.get(pk=pk))

    return HttpResponseRedirect("/EMR/" + str(patient.id))


def emr(request, pk):
    """
    EMR
    :param request:
    :param pk: primary key for emr
    :return: render
    """
    user_type = get_user_type(request.user)
    if user_type == "patient":
        emr = EMR_Entry.objects.filter(patient__id=pk, shown=True)
    else:
        emr = EMR_Entry.objects.filter(patient_id=pk)
    hospitals = []
    if user_type == "doctor":
        hospitals = Hospital.objects.filter(doctor=Doctor.objects.get(user=request.user))
    elif user_type == "admin":
        hospitals = Hospital.objects.filter(hospital_admin=Hospital_Admin.objects.get(user=request.user))

    emr = list(reversed(emr))
    patient = Patient.objects.get(pk=pk)

    current_prescriptions = Prescription.objects.filter(patient__user=patient.user, prescribed=True)
    current_prescriptions = list(reversed(current_prescriptions))
    past_prescriptions = Prescription.objects.filter(patient__user=patient.user, prescribed=False)
    past_prescriptions = list(reversed(past_prescriptions))
    unreleased_tests = Test.objects.filter(patient__user=patient.user, released=False)
    unreleased_tests = list(reversed(unreleased_tests))
    released_tests = Test.objects.filter(patient__user=patient.user, released=True)
    released_tests = list(reversed(released_tests))
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-start_time')
    return render(request, 'HealthApps/electronic_medical_record.html', {
        'emr': emr,
        'patient': patient,
        'current_prescriptions': current_prescriptions,
        'past_prescriptions': past_prescriptions,
        'unreleased_tests': unreleased_tests,
        'released_tests': released_tests,
        'appointments': appointments,
        'hospitals': hospitals,
        'user_type': user_type})


def emr_entry(request, pk):
    """
    EMR entry
    :param request:
    :param pk: emr primary key
    :return: render
    """
    emr_entry = EMR_Entry.objects.get(pk=pk)
    return render(request, 'HealthApps/emr_entry.html', {'emr_entry': emr_entry, 'user_type': get_user_type(request.user)})


def get_prescription(request, pk):
    """
    gets prescription
    :param request:
    :param pk: the primary key for the prescription
    :return:
    """
    prescription = Prescription.objects.get(pk=pk)
    return render(request, 'HealthApps/prescription.html', {'prescription': prescription, 'user_type': get_user_type(request.user)})


def get_test(request, pk):
    """
    gets the test
    :param request:
    :param pk: the primary key for the test
    :return:
    """
    test = Test.objects.get(pk=pk)
    return render(request, 'HealthApps/test.html', {'test': test, 'user_type': get_user_type(request.user)})


class CreateEMREntry:
    """
    Creates the EMR Entry
    """
    def emr_transfer(patient, old_hospital, new_hospital):
        """
        tansfers the emr
        :param old_hospital: the old hospital
        :param new_hospital: the new hospital
        :return:
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + " was transferred from " + old_hospital.name + " to " + new_hospital.name

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, description=description, type="Transfer", shown=True)

    def emr_test_create(test):
        """
        Creates the emr
        :return:
        """
        timestamp = datetime.now()
        patient = test.patient
        description = patient.user.first_name + " " + patient.user.last_name + " had " + test.name + " performed"

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, test=test, description=description, type="Test Create")

    def emr_test_release(test):
        """
        Releases the test
        :return:
        """
        timestamp = datetime.now()
        patient = test.patient
        description = test.name + " was released to " + patient.user.first_name + " " + patient.user.last_name

        other_entry = EMR_Entry.objects.filter(test__id=test.id)[0]
        other_entry.shown = True
        other_entry.save()

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, test=test, description=description, type="Test Release", shown=True)

    def emr_prescription_create(prescription):
        """
        Creates the prescription
        :return:
        """
        timestamp = datetime.now()
        patient = prescription.patient
        description = patient.user.first_name + " " + patient.user.last_name + " was prescribed " + prescription.name

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, prescription=prescription, description=description, type="Prescribe Prescription", shown=True)

    def emr_prescription_delete(prescription):
        """
        Deletes the pescription
        :return:
        """
        timestamp = datetime.now()
        patient = prescription.patient
        description = patient.user.first_name + " " + patient.user.last_name + " had prescription " + prescription.name + " deleted"

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, prescription=prescription, description=description, type="Delete Prescription", shown=True)

    def emr_admit(patient, hospital):
        """
        admits the emr
        :param hospital: the hospital
        :return:
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + " was admitted to " + hospital.name

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, description=description, type="Admit", shown=True)

    def emr_discharge(patient, hospital):
        """
        discharges the emr
        :param hospital: the hospital
        :return:
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + " was discharged from " + hospital.name

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, description=description, type="Discharge", shown=True)

    def emr_vitals_edit(patient):
        """
        Edits the vitals
        :return:
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + "'s vitals were changed"

        EMR_Entry.objects.create(timestamp=timestamp, patient=patient, description=description, type="Edit Vitals", shown=True)
