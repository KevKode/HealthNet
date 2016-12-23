"""
file: utils.py
description: provides various utility functions to be used throughout project
"""


from .models import Patient, Doctor, Nurse, Hospital_Admin, Hospital
from django.contrib.auth.models import User
from collections import defaultdict


def is_hospital_admin(user):
    """
    Gets whether the specified user is a hospital admin
    :param user: the specified user
    :return: whether or not the specified user is hospital admin
    """
    if user.is_authenticated():
        return get_user_type(user) == 'admin'
    return False


def get_user_type(user):
    """
    Gets the type of the specified user
    :param user: the specified user
    :return: the user's type
    """
    if str(user) == 'AnonymousUser':
        return 'anon'
    else:
        type_user = ""

        pat_check = Patient.objects.filter(user=user)
        doc_check = Doctor.objects.filter(user=user)
        nur_check = Nurse.objects.filter(user=user)
        admin_check = Hospital_Admin.objects.filter(user=user)

        if len(pat_check) != 0:
            type_user = pat_check[0].get_type()
        elif len(doc_check) != 0:
            type_user = doc_check[0].get_type()
        elif len(nur_check) != 0:
            type_user = nur_check[0].get_type()
        elif len(admin_check) != 0:
            type_user = admin_check[0].get_type()

        return type_user


def export_data(filename='data.csv'):
    """
    Exports database information into a csv
    :param filename: the csv to write to
    :return: n/a
    """
    file = open(filename, 'w')
    data_string = ''
    for user in User.objects.all():
        user_string = '[User]'
        user_string += '{username},' + user.username
        user_string += ',{email},' + user.username
        user_string += ',{password},' + user.password
        user_string += ',{first_name},' + (user.first_name if user.first_name else '')
        user_string += ',{last_name},' + (user.last_name if user.last_name else '')
        user_string += ',{is_staff},' + ('1' if user.is_staff else '0')
        user_string += ',{is_superuser},' + ('1' if user.is_superuser else '0')
        user_string += ',{is_active},' + ('1' if user.is_active else '0')
        data_string += user_string + '\n'
    for hospital in Hospital.objects.all():
        hospital_string = '[Hospital]'
        hospital_string += '{name},' + hospital.name
        data_string += hospital_string + '\n'
    for hadmin in Hospital_Admin.objects.all():
        hadmin_string = '[Hospital_Admin]'
        hadmin_string += '{username},' + hadmin.user.username
        hadmin_string += ',{hospital},' + hadmin.hospital.name
        data_string += hadmin_string + '\n'
    for doctor in Doctor.objects.all():
        doctor_string = '[Doctor]'
        doctor_string += '{username},' + doctor.user.username
        doctor_string += ',{hospitals},'
        for hospital in Doctor.objects.get(user__username=doctor.user.username).hospitals.all():
            doctor_string += hospital.name + ','
        doctor_string += '{max_patients},' + str(doctor.max_patients)
        doctor_string += ',{cur_patients},' + str(doctor.cur_patients)
        data_string += doctor_string + '\n'
    for nurse in Nurse.objects.all():
        nurse_string = '[Nurse]'
        nurse_string += '{username},' + nurse.user.username
        nurse_string += ',{hospitals},'
        for hospital in Nurse.objects.get(user__username=nurse.user.username).hospitals.all():
            nurse_string += hospital.name + ','
        nurse_string += '{doctors},'
        for doctor in Nurse.objects.get(user__username=nurse.user.username).doctors.all():
            nurse_string += doctor.user.username + ','
        data_string += nurse_string + '\n'
    for patient in Patient.objects.all():
        patient_string = '[Patient]'
        patient_string += '{username},' + patient.user.username
        patient_string += ',{insurance_number},' + patient.insurance_number
        patient_string += ',{hospital},' + patient.hospital.name
        patient_string += ',{admitted_to},' + (patient.admitted_to if patient.admitted_to else '')
        patient_string += ',{doctor},' + patient.doctor.user.username
        patient_string += ',{emergency_name},' + patient.emergency_name
        patient_string += ',{emergency_number},' + patient.emergency_number
        patient_string += ',{transfer_to},' + (patient.transfer_to if patient.transfer_to else '')
        patient_string += ',{height},' + (str(patient.height) if patient.height else '')
        patient_string += ',{weight},' + (str(patient.weight) if patient.weight else '')
        patient_string += ',{cholesterol},' + (patient.cholesterol if patient.cholesterol else '')
        patient_string += ',{pulse},' + (str(patient.pulse) if patient.pulse else '')
        patient_string += ',{temperature},' + (str(patient.temperature) if patient.temperature else '')
        patient_string += ',{blood_pressure},' + (patient.blood_pressure if patient.blood_pressure else '')
        patient_string += ',{blood_type},' + (patient.blood_type if patient.blood_type else '')
        data_string += patient_string + '\n'

    file.write(data_string)

    file.close()


def is_key(data):
    """
    Returns whether or not the given string is a key
    :param data: specified string
    :return: whether or not data is a key
    """
    return data.startswith("{") and data.endswith("}")


def import_user(data):
    """
    Imports user from data
    :param data: hash of model fields and their values
    :return: n/a
    """
    if not User.objects.filter(username=data['username'][0]).exists():
        user = User.objects.create(
            username=data['username'][0],
            password=data['password'][0],
            first_name=data['first_name'][0],
            last_name=data['last_name'][0],
            is_staff=int(data['is_staff'][0]),
            is_superuser=int(data['is_superuser'][0]),
            is_active=int(data['is_active'][0]),
        )
        user.save()


def import_hospital(data):
    """
    Imports hospital from data
    :param data: hash of model fields and their values
    :return: n/a
    """
    if not Hospital.objects.filter(name=data['name'][0]).exists():
        hospital = Hospital.objects.create(
            name=data['name'][0],
        )
        hospital.save()


def import_hadmin(data):
    """
    Imports hospital admin from data
    :param data: hash of model fields and their values
    :return: n/a
    """
    if not Hospital_Admin.objects.filter(user__username=data['username'][0]).exists():
        hadmin = Hospital_Admin.objects.create(
            user=User.objects.get(username=data['username'][0]),
            hospital=Hospital.objects.get(name=data['hospital'][0]),
        )
        hadmin.save()


def import_nurse(data):
    """
    Imports nurse from data
    :param data: hash of model fields and their values
    :return: n/a
    """
    if not Nurse.objects.filter(user__username=data['username'][0]).exists():
        nurse = Nurse.objects.create(
            user=User.objects.get(username=data['username'][0]),
        )
        for hospital in data['hospitals']:
            if Hospital.objects.filter(name=hospital).exists():
                hospital_obj = Hospital.objects.get(name=hospital)
                nurse.hospitals.add(hospital_obj)
        for doctor in data['doctors']:
            if Doctor.objects.filter(user__username=doctor).exists():
                doctor_obj = Doctor.objects.get(user__username=doctor)
                nurse.doctors.add(doctor_obj)
        nurse.save()


def import_doctor(data):
    """
    Imports doctor from data
    :param data: hash of model fields and their values
    :return: n/a
    """
    if not Doctor.objects.filter(user__username=data['username'][0]).exists():
        doctor = Doctor.objects.create(
            user=User.objects.get(username=data['username'][0]),
            max_patients=int(data['max_patients'][0]),
            cur_patients=int(data['cur_patients'][0]),
        )
        for hospital in data['hospitals']:
            if Hospital.objects.filter(name=hospital).exists():
                hospital_obj = Hospital.objects.get(name=hospital)
                doctor.hospitals.add(hospital_obj)
        doctor.save()


def import_patient(data):
    """
    Imports patient from data
    :param data: hash of model fields and their values
    :return: n/a
    """
    if not Patient.objects.filter(user__username=data['username'][0]).exists():
        patient = Patient.objects.create(
            insurance_number=data['insurance_number'][0],
            hospital=Hospital.objects.get(name=data['hospital'][0]),
            doctor=Doctor.objects.get(user__username=data['doctor'][0]),
            user=User.objects.get(username=data['username'][0]),
            emergency_name=data['emergency_name'][0],
            emergency_number=data['emergency_number'][0],
        )

        if Hospital.objects.filter(name=data['admitted_to'][0]).exists():
            patient.admitted_to = Hospital.objects.get(name=data['admitted_to'][0])

            hospital = Hospital.objects.get(name=data['admitted_to'][0])
            hospital.admitted_patients.add(patient)
            hospital.save()

        if Hospital.objects.filter(name=data['transfer_to'][0]).exists():
            patient.transfer_to = Hospital.objects.get(name=data['transfer_to'][0])

        if len(data['height'][0]) > 0:
            patient.height = float(data['height'][0])
        if len(data['weight'][0]) > 0:
            patient.weight = float(data['weight'][0])
        if len(data['cholesterol'][0]) > 0:
            patient.cholesterol = data['cholesterol'][0]
        if len(data['pulse'][0]) > 0:
            patient.pulse = int(data['pulse'][0])
        if len(data['temperature'][0]) > 0:
            patient.temperature = float(data['temperature'][0])
        if len(data['blood_pressure'][0]) > 0:
            patient.blood_pressure = data['blood_pressure'][0]
        if len(data['blood_type'][0]) > 0:
            patient.blood_type = data['blood_type'][0]
        patient.save()


def import_data(filename='data.csv'):
    """
    Imports data from csv into database
    :param filename: the specified csv
    :return: n/a
    """
    file = open(filename)
    for line in file:
        line = line.strip()
        data_type = line.split(',')[0].split(']')[0][1:]
        data = line.split(']')[1].split(',')

        fields = defaultdict(list)
        current_field = ""
        for val in data:
            if is_key(val):
                current_field = val[1:-1]
            else:
                fields[current_field].append(val)
        if data_type == "User":
            import_user(fields)
        elif data_type == "Hospital":
            import_hospital(fields)
        elif data_type == "Hospital_Admin":
            import_hadmin(fields)
        elif data_type == "Nurse":
            import_nurse(fields)
        elif data_type == "Doctor":
            import_doctor(fields)
        elif data_type == "Patient":
            import_patient(fields)
