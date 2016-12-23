"""
file: log_item.py
description: view and functions for log items
"""

from django.shortcuts import render
from datetime import datetime

from ..models import LogItem, Patient
from ..utils import get_user_type


def log_table(request):
    """
    View for log table
    :param request: request to get user type
    :return: rendered template
    """
    log_items = list(reversed(LogItem.objects.all()))
    return render(request, 'HealthApps/log_table.html', dict(log_items=log_items, user_type=get_user_type(request.user)))


def view_log_item(request, pk):
    """
    View for specific log item
    :param request: request to get user type
    :param pk: primary key of specific log item
    :return: rendered template
    """
    log_item = LogItem.objects.get(pk=pk)
    return render(request, 'HealthApps/log_item.html', dict(log_item=log_item, user_type=get_user_type(request.user)))


class CreateLogItem:
    """
    Log item creation
    """
    def li_patient_create(new_user):
        """
        Creates a log item for patient creation
        :return: log item
        """
        timestamp = datetime.now()
        description = "Patient " + new_user.first_name + " " + new_user.last_name + " was created"
        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

        return new_item

    def li_patient_edit(new_model, old_model):
        """
        Creates a log item for patient editing
        :return: log item
        """
        timestamp = datetime.now()
        verbose_description = CreateLogItem.what_changed(new_model, old_model)
        if isinstance(new_model, Patient)and isinstance(old_model, Patient):
            description = "Patient " + old_model.user.first_name + " " + old_model.user.last_name + " was edited"
        else:
            description = "Patient " + old_model.first_name + " " + old_model.last_name + " was edited"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

        return new_item

    def li_appointment_create(user, appointment):
        """
        Creates a log item for appointment creation
        :param appointment: the specific appointment
        :return: log item
        """
        timestamp = datetime.now()
        if get_user_type(user) == "patient":
            description = "Patient " + user.first_name + " " + user.last_name + " created an appointment with Doctor " + appointment.doctor.user.first_name + " " + appointment.doctor.user.last_name
        elif get_user_type(user) == "doctor":
            description = "Doctor " + user.first_name + " " + user.last_name + " created an appointment with Patient " + appointment.patient.user.first_name + " " + appointment.patient.user.last_name
        elif get_user_type(user) == "nurse":
            description = "Nurse " + user.first_name + " " + user.last_name + " created an appointment with Patient " + appointment.patient.user.first_name + " " + appointment.patient.user.last_name + " and Doctor " + appointment.doctor.user.first_name + " " + appointment.doctor.user.last_name

        verbose_description = description + " in " + appointment.hospital.name + " on " + appointment.date.strftime("%Y-%m-%d") + " starting at " + appointment.start_time.strftime("%H:%M:%S") + " and ending at " + appointment.end_time.strftime("%H:%M:%S")

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

        return new_item

    def li_appointment_edit(user, new_appointment, old_appointment):
        """
        Creates log item for appointment edit
        :param new_appointment: the updated appointment
        :param old_appointment: the outdated appointment
        :return: log item
        """
        timestamp = datetime.now()
        description = get_user_type(user).title() + " " + user.first_name + " " + user.last_name + " edited an appointment"
        verbose_description = CreateLogItem.what_changed(new_appointment, old_appointment)

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

        return new_item

    def li_appointment_cancel(user, appointment):
        """
        Creates log item for appointment cancellation
        :param appointment: the specific appointment
        :return: log item
        """
        timestamp = datetime.now()
        if get_user_type(user) == "patient":
            description = "Patient " + user.first_name + " " + user.last_name + " cancelled an appointment with Doctor " + appointment.doctor.user.first_name + " " + appointment.doctor.user.last_name
        elif get_user_type(user) == "doctor":
            description = "Doctor " + user.first_name + " " + user.last_name + " cancelled an appointment with Patient " + appointment.patient.user.first_name + " " + appointment.patient.user.last_name
        elif get_user_type(user) == "nurse":
            description = "Nurse " + user.first_name + " " + user.last_name + " cancelled an appointment with Patient " + appointment.patient.user.first_name + " " + appointment.patient.user.last_name + " and Doctor " + appointment.doctor.user.first_name + " " + appointment.doctor.user.last_name

        verbose_description = description + " in " + appointment.hospital.name + " on " + appointment.date.strftime("%Y-%m-%d") + " starting at " + appointment.start_time.strftime("%H:%M:%S") + " and ending at " + appointment.end_time.strftime("%H:%M:%S")

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

        return new_item

    def li_hospital_create(user, hospital):
        """
        Creates log item for hospital creation
        :param hospital: the specified hospital
        :return: log item
        """
        timestamp = datetime.now()
        if user.is_superuser:
            description = "System Administrator created " + hospital.name
        else:
            description = user.first_name + " " + user.last_name + " created " + hospital.name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

        return new_item

    def li_doctor_create(new_user):
        """
        Creates log item for doctor creation
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + new_user.first_name + " " + new_user.last_name + " was created"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

        return new_item

    def li_nurse_create(new_user):
        """
        Creates log item for nurse creation
        :return: log item
        """
        timestamp = datetime.now()
        description = "Nurse " + new_user.first_name + " " + new_user.last_name + " was created"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

        return new_item

    def li_hadmin_create(new_user):
        """
        Creates log item for hospital admin creation
        :return: log item
        """
        timestamp = datetime.now()
        description = "Hospital Administrator " + new_user.first_name + " " + new_user.last_name + " was created"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_test_create(test):
        """
        Creates log item for test creation
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + test.doctor.user.first_name + " " + test.doctor.user.last_name + " created " + test.name + " test result"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_test_release(test):
        """
        Creates log item for test release
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + test.doctor.user.first_name + " " + test.doctor.user.last_name + " released " + test.name + " test results to Patient " + test.patient.user.first_name + " " + test.patient.user.last_name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_prescription_create(prescription):
        """
        Creates log item for prescription creation
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + prescription.doctor.user.first_name + " " + prescription.doctor.user.last_name + " prescribed "  + prescription.name + " for Patient " + prescription.patient.user.first_name + " " + prescription.patient.user.last_name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_prescription_delete(prescription):
        """
        Creates log item for prescription deletion
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + prescription.doctor.user.first_name + " " + prescription.doctor.user.last_name + " ended " + prescription.name + " prescription for Patient " + prescription.patient.user.first_name + " " + prescription.patient.user.last_name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_vitals_edit(patient):
        """
        Creates log item for vitals editing
        :return: log item
        """
        timestamp = datetime.now()
        description = "Patient " + patient.user.first_name + " " + patient.user.last_name + "'s vitals were changed"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_custom_entry_create(user, entry):
        """
        Creates log item for entry creation
        :param entry: specified entry
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + user.first_name + " " + user.last_name + " created a custom EMR entry for Patient " + entry.patient.user.first_name + " " + entry.patient.user.last_name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_doctor_approve(doctor):
        """
        Creates log item for doctor approval
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + doctor.user.first_name + " " + doctor.user.last_name + " was approved to use HealthNet"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_nurse_approve(nurse):
        """
        Creates log item for nurse approval
        :return: log item
        """
        timestamp = datetime.now()
        description = "Nurse " + nurse.user.first_name + " " + nurse.user.last_name + " was approved to use HealthNet"

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_block_off_create(user, block):
        """
        Creates log item for block off creation
        :param block: time block
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + user.first_name + " " + user.last_name + " created a block off"
        verbose_description = description + " on " + block.date.strftime("%Y-%m-%d") + " starting at " + block.start_time.strftime("%H:%M:%S") + " and ending at " + block.end_time.strftime("%H:%M:%S")

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

    def li_block_off_edit(user, new_block, old_block):
        """
        Creates log item for block off edit
        :param new_block: updated time block
        :param old_block: outdated time block
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + user.first_name + " " + user.last_name + " edited a block off"
        verbose_description = CreateLogItem.what_changed(new_block, old_block)

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

    def li_block_off_cancel(user, block):
        """
        Creates log item for block off cancel
        :param block: time block
        :return: log item
        """
        timestamp = datetime.now()
        description = "Doctor " + user.first_name + " " + user.last_name + " cancelled a block off"

        verbose_description = description + " on " + block.date.strftime("%Y-%m-%d") + " starting at " + block.start_time.strftime("%H:%M:%S") + " and ending at " + block.end_time.strftime("%H:%M:%S")

        new_item = LogItem.objects.create(timestamp=timestamp, description=description, verbose_description=verbose_description)
        new_item.save()

    def li_admit(patient, hospital):
        """
        Creates log item for patient admittance
        :param hospital: specified hospital
        :return: log item
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + " was admitted to " + hospital.name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_discharge(patient, hospital):
        """
        Creates log item for patient discharge
        :param hospital: specified hospital
        :return: log item
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + " was discharged from " + hospital.name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def li_transfer(patient, old_hospital, new_hospital):
        """
        Creates log item for patient transfer
        :param old_hospital: original patient hospital
        :param new_hospital: new patient hospital
        :return: log item
        """
        timestamp = datetime.now()
        description = patient.user.first_name + " " + patient.user.last_name + " was transferred from " + old_hospital.name + " to " + new_hospital.name

        new_item = LogItem.objects.create(timestamp=timestamp, description=description)
        new_item.save()

    def what_changed(new_model, old_model):
        """
        Describes what changed between the old and new model
        :param old_model: the old model
        :return: the change
        """
        what_changed = ""

        new_fields = new_model._meta.get_fields()

        changes = filter(lambda field: getattr(new_model, field.name, None) != getattr(old_model, field.name, None), new_fields)

        for change in changes:
            what_changed += change.name + " was changed from {} to {}, ".format(getattr(old_model, change.name), getattr(new_model, change.name))

        return what_changed[:-2]

