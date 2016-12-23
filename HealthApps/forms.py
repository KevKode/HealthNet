"""
file: forms.py
description: model and regular forms for all register and update related components
"""

from django.contrib.auth import authenticate
from django.db.models.fields import BLANK_CHOICE_DASH
from django import forms
from django.core.validators import *

from .views.log_item import CreateLogItem
from .models import Appointment, Test, Prescription, EMR_Entry
from .utils import *


class PatientForm(forms.ModelForm):
    """
    Form for patient registration
    """
    insurance_number = forms.CharField(required=True,
                                       validators=[
                                           RegexValidator(
                                               regex='^[A-Z]\w{12}$',
                                               message="Insurance Number Format: One capital letter followed by 12 "
                                                       "alphanumeric characters. (Ex: A12Z45f78s012) "
                                           ),
                                       ])
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    username = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    height = forms.FloatField(required=False, min_value=6, max_value=108),
    weight = forms.FloatField(required=False, min_value=0.5, max_value=1500),
    cholesterol = forms.CharField(required=False,
                                  validators=[
                                      RegexValidator(
                                          regex="^(9[0-9]|1[0-9][0-9]|200)\/(100|2[5-9]|[3-9][0-9])$",
                                          message="Please input a valid LDL/HDL. "
                                                  "LDL must be between 90 and 200, HDL must be between 25 and 100."
                                      )
                                  ])
    pulse = forms.IntegerField(required=False, min_value=25, max_value=250)
    temperature = forms.FloatField(required=False, min_value=55, max_value=120)
    blood_pressure = forms.CharField(required=False,
                                     validators=[
                                         RegexValidator(
                                             regex="^(180|1[0-7][0-9])\/(120|[6-9][0-9]|1[0-1][0-9])$",
                                             message="Please input a valid Systolic/Diastolic blood pressure. "
                                                     "Systolic must be between 100 and 180, Diastolic must be between "
                                                     "60 and 120."
                                         )
                                     ])
    blood_types = (('O', 'O'),
                   ('A', 'A'),
                   ('B', 'B'),
                   ('AB', 'AB'))
    blood_type = forms.ChoiceField(required=False, choices=BLANK_CHOICE_DASH + list(blood_types))
    emergency_name = forms.CharField(required=True)
    emergency_number = forms.CharField(required=True,
                                       validators=[
                                           RegexValidator(
                                               regex="^(\(\d{3}\)|\d{3})?[- \.]?(\d{3})[- \.]?(\d{4})$",
                                               message="Please input a valid phone number."
                                           )
                                       ])
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all().order_by('name'), empty_label=None)

    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), empty_label=None)

    def clean_insurance_number(self):
        """
        Verifies that insurance number is unique
        :return: cleaned insurance number
        """
        insurance = self.cleaned_data['insurance_number']

        if Patient.objects.exclude(pk=self.instance.pk).filter(insurance_number=insurance).exists():
            raise forms.ValidationError('Someone has already registered with insurance number "%s"' % insurance)

        return insurance

    def clean_username(self):
        """
        Verifies that username is unique
        :return: cleaned username
        """
        username = self.cleaned_data['username']

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Username "%s" is already in use.' % username)

        return username

    def clean_password_confirm(self):
        """
        Verifies that passwords are matching
        :return: cleaned password_confirm
        """
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return password_confirm

    def save(self, commit=True):
        """
        Saves new patient, increments doctor patient count, and creates log item
        :param commit: whether or not to commit the patient to the database
        :return: the saved patient
        """
        patient = super(PatientForm, self).save(commit=False)

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        if commit:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            patient.user = user

            patient.save()

            doctor = patient.doctor
            doctor.cur_patients += 1
            doctor.save()

            CreateLogItem.li_patient_create(user)

        patient.hospital = self.cleaned_data["hospital"]

        return patient

    def __init__(self, *args, **kwargs):
        """
        Initializes patient form and does cascading select for hospital -> doctor selection
        :param args: form arguments
        :param kwargs: form kwarguments
        """
        super(PatientForm, self).__init__(*args, **kwargs)
        hospitals = Hospital.objects.all()
        if len(hospitals) == 1:
            self.fields['hospital'].inital = hospitals[0].pk

        hospital_id = self.fields['hospital'].initial or self.initial.get('hospital') or self['hospital'].value()
        if hospital_id:
            doctors = Doctor.objects.filter(hospitals__id__in=hospital_id)
            self.fields['doctor'].queryset = doctors
            if len(doctors) == 1:
                self.fields['doctor'].initial = doctors[0].pk

    class Meta:
        """
        Information about patient model for form
        """
        model = Patient

        fields = ["insurance_number", 'first_name', 'last_name', 'username', 'password', "hospital", 'doctor', 'height',
                  'weight', 'cholesterol', 'pulse', 'temperature', 'blood_pressure', 'blood_type', 'emergency_name',
                  'emergency_number']


class HospitalAdminForm(forms.ModelForm):
    """
    Form for Hospital Administrator Registration
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    username = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all().order_by('name'), empty_label=None)

    def __init__(self, *args, **kwargs):
        """
        Adds user to self object
        :param args: arguments
        :param kwargs: kwarguments
        """
        self.user = kwargs.pop('user', None)
        super(HospitalAdminForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Verifies that username is unique
        :return: cleaned username
        """
        username = self.cleaned_data['username']

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Username "%s" is already in use.' % username)

        return username

    def clean_password_confirm(self):
        """
        Verifies that passwords are matching
        :return: cleaned password_confirm
        """
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return password_confirm

    def save(self, commit=True):
        """
        Saves hospital administrator and creates log item
        :param commit: whether or not to commit admin to database
        :return: saved hospital admin
        """
        hospital_admin = super(HospitalAdminForm, self).save(commit=False)

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        if commit:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            hospital_admin.user = user
            hospital_admin.save()

            CreateLogItem.li_hadmin_create(user)

        hospital_admin.hospital = self.cleaned_data["hospital"]

        return hospital_admin

    class Meta:
        """
        Information about hospital admin model for form
        """
        model = Hospital_Admin
        fields = ['first_name', 'last_name', 'username', 'password', "hospital"]


class NurseForm(forms.ModelForm):
    """
    Form for Nurse Registration
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    username = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    hospitals = forms.ModelMultipleChoiceField(queryset=Hospital.objects.all().order_by('name'))
    doctors = forms.ModelMultipleChoiceField(queryset=Doctor.objects.all())

    def __init__(self, *args, **kwargs):
        """
        Adds user to self user object
        :param args: arguments
        :param kwargs: kwarguments
        """
        self.user = kwargs.pop('user')
        super(NurseForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Verifies username is unique
        :return: cleaned username
        """
        username = self.cleaned_data['username']

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Username "%s" is already in use.' % username)

        return username

    def clean_password_confirm(self):
        """
        Verifies passwords matching
        :return: cleaned password_confirm
        """
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return password_confirm

    def save(self, commit=True):
        """
        Saves nurse (enabled/disabled based on auth) and creates log item
        :param commit: whether or not to commit nurse to database
        :return: saved nurse
        """
        nurse = super(NurseForm, self).save(commit=False)

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        if commit:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            if self.user.is_authenticated() and (self.user.is_superuser or get_user_type(self.user) == "admin"):
                user.is_active = True
            else:
                user.is_active = False

            user.save()

            nurse.user = user

            nurse.save()
            CreateLogItem.li_nurse_create(user)

        nurse.hospitals = self.cleaned_data["hospitals"]
        nurse.doctors = self.cleaned_data['doctors']

        return nurse

    class Meta:
        """
        Information about nurse model for form
        """
        model = Nurse
        fields = ['first_name', 'last_name', 'username', 'password', "hospitals", 'doctors']


class DoctorForm(forms.ModelForm):
    """
    Form for Doctor Registration
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    username = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    hospitals = forms.ModelMultipleChoiceField(queryset=Hospital.objects.all().order_by('name'))
    max_patients = forms.NumberInput()

    def __init__(self, *args, **kwargs):
        """
        Adds user to self object
        :param args: arguments
        :param kwargs: kwarguments
        """
        self.user = kwargs.pop('user')
        super(DoctorForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Verifies username is unique
        :return: cleaned username
        """
        username = self.cleaned_data['username']

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Username "%s" is already in use.' % username)

        return username

    def clean_password_confirm(self):
        """
        Verifies passwords match
        :return: cleaned password_confirm
        """
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return password_confirm

    def save(self, commit=True):
        """
        Saves doctor (enabled/disabled based on auth) and creates log item
        :param commit: whether or not to save doctor to database
        :return: saved doctor
        """
        doctor = super(DoctorForm, self).save(commit=False)

        doctor.max_patients = self.cleaned_data['max_patients']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        if commit:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            if self.user.is_authenticated() and (self.user.is_superuser or get_user_type(self.user) == "admin"):
                user.is_active = True
            else:
                user.is_active = False

            user.save()

            doctor.user = user

            doctor.save()
            CreateLogItem.li_doctor_create(user)

        doctor.hospitals = self.cleaned_data["hospitals"]

        return doctor

    class Meta:
        """
        Doctor model information for form
        """
        model = Doctor
        fields = ['first_name', 'last_name', 'username', 'password', "hospitals", 'max_patients']


class HospitalForm(forms.ModelForm):
    """
    Form for Hospital Creation
    """
    # @TODO Add verification for hospital creation
    def clean_name(self):
        """
        Verifies name is unique
        :return: cleaned name
        """
        name = self.cleaned_data['name']
        if Hospital.objects.exclude(pk=self.instance.pk).filter(name=name).exists():
            raise forms.ValidationError('%s is already registered.' % name)
        return name

    class Meta:
        """
        Hospital model information for form
        """
        model = Hospital
        fields = ['name']


class UserInfoForm(forms.ModelForm):
    """
    Form for user info in transfer
    """
    username = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        """
        User model information for form
        """
        model = User
        fields = ['first_name', 'last_name', 'username']


class ProfileForm(forms.ModelForm):
    """
    Form for profile updating
    """

    emergency_name = forms.CharField(required=True)
    emergency_number = forms.CharField(required=True,
                                       validators=[
                                           RegexValidator(
                                               regex="^(\(\d{3}\)|\d{3})?[- \.]?(\d{3})[- \.]?(\d{4})$",
                                               message="Please input a valid phone number."
                                           )
                                       ])

    class Meta:
        """
        Patient model information for form
        """
        model = Patient
        fields = ['emergency_name', 'emergency_number']

    def __init__(self, *args, **kwargs):
        """
        Initializes appointment data
        :param args: arguments
        :param kwargs: kwarguments
        """
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['emergency_name'].widget.attrs = {'class': 'form-control'}
        self.fields['emergency_number'].widget.attrs = {'class': 'form-control'}

class UserForm(forms.ModelForm):
    """
    Form for profile updating
    """
    class Meta:
        """
        Patient model information for form
        """
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        """
        Initializes appointment data
        :param args: arguments
        :param kwargs: kwarguments
        """
        user = kwargs.pop('user', None)
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'] = forms.EmailField()
        self.fields['username'].widget.attrs = {'class': 'form-control'}


class LoginForm(forms.ModelForm):
    """
    Form for logging in
    """
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        """
        Verifies user can log in
        :return: cleaned login data
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        """
        Logs into django system
        :param request: currently unused
        :return: logged in user
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user

    class Meta:
        """
        User model information for form
        """
        model = User
        fields = ['username', "password"]


class AppointmentForm(forms.ModelForm):
    """
    Form for appointments
    """
    class Meta:
        """
        Appointment model information for form
        """
        model = Appointment
        date = forms.DateField()
        start_time = forms.TimeField()
        end_time = forms.TimeField()

        fields = ['date', 'start_time', 'end_time', 'patient', 'description']

    def __init__(self, *args, **kwargs):
        """
        Initializes appointment data
        :param args: arguments
        :param kwargs: kwarguments
        """
        user = kwargs.pop('user', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs = {'class': 'form-control'}
        self.fields['start_time'].widget.attrs = {'class': 'form-control'}
        self.fields['end_time'].widget.attrs = {'class': 'form-control'}
        self.fields['description'].widget.attrs = {'class': 'form-control'}

        if user and (len(Patient.objects.filter(user=user))) != 0:
            self.fields['end_time'] = forms.TimeField(required=False, widget=forms.HiddenInput(), initial='00:00:00')
            self.fields['patient'] = forms.ModelChoiceField(required=False, widget=forms.HiddenInput(),
                                                            initial=Patient.objects.filter(user=user)[0],
                                                            queryset=Patient.objects.filter(user=user))
        elif user and (len(Doctor.objects.filter(user=user)) != 0):
            self.fields['patient'].queryset = Patient.objects.filter(doctor=Doctor.objects.filter(user=user)[0])
            self.fields['patient'].widget.attrs = {'class': 'form-control'}

        elif user and (len(Nurse.objects.filter(user=user)) != 0):
            self.fields['patient'].queryset = Patient.objects.filter(
                doctor__in=Doctor.objects.filter(nurse=Nurse.objects.filter(user=user)[0]))


class StatisticsForm(forms.Form):  # Note that it is not inheriting from forms.ModelForm
    """
    Form for system statistics
    """
    start_date = forms.DateField()
    end_date = forms.DateField()
    fields = ['start_date', 'end_date']


class PrescriptionForm(forms.ModelForm):
    """
    Form for prescriptions
    """
    class Meta:
        """
        Prescription model information for form
        """
        model = Prescription
        fields = ['name', 'dosage_amount', 'dosage_unit', 'frequency_amount', 'frequency_unit']


class TestForm(forms.ModelForm):
    """
    Form for tests
    """
    class Meta:
        """
        Test model information for form
        """
        model = Test
        fields = ['name', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes test form
        :param args: arguments
        :param kwargs: kwarguments
        """
        super(TestForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class': 'form-control'}
        self.fields['description'].widget.attrs = {'class': 'form-control'}


class EMRForm(forms.ModelForm):
    """
    Form for EMRs
    """
    class Meta:
        """
        EMR_Entry model information for form
        """
        model = EMR_Entry
        fields = ['type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes EMRForm data
        :param args:
        :param kwargs:
        """
        super(EMRForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs = {'class': 'form-control'}
        self.fields['description'].widget.attrs = {'class': 'form-control'}


class VitalsForm(forms.ModelForm):
    """
    Form for vitals
    """
    class Meta:
        """
        Patient model information for form
        """
        model = Patient
        fields = ['height', 'weight', 'cholesterol', 'pulse', 'temperature', 'blood_pressure', 'blood_type']

    def __init__(self, *args, **kwargs):
        """
        Initializes vital form information
        :param args: arguments
        :param kwargs: kwarguments
        """
        super(VitalsForm, self).__init__(*args, **kwargs)
        self.fields['height'] = forms.FloatField(max_value=108, min_value=6, required=False)
        self.fields['height'].widget.attrs = {'class': 'form-control'}
        self.fields['weight'] = forms.FloatField(max_value=1500, min_value=0.5, required=False)
        self.fields['weight'].widget.attrs = {'class': 'form-control'}
        self.fields['cholesterol'].widget.attrs = {'class': 'form-control'}
        self.fields['pulse'] = forms.FloatField(max_value=120, min_value=25, required=False)
        self.fields['pulse'].widget.attrs = {'class': 'form-control'}
        self.fields['temperature'] = forms.FloatField(max_value=120.0, min_value=55.0, required=False)
        self.fields['temperature'].widget.attrs = {'class': 'form-control'}
        self.fields['blood_pressure'].widget.attrs = {'class': 'form-control'}
        self.fields['blood_type'].widget.attrs = {'class': 'form-control'}


class BlockOffForm(forms.ModelForm):
    """
    Form for blocking off time for doctors
    """
    recurring = forms.BooleanField()
    weeks = forms.IntegerField()

    class Meta:
        """
        Appointment model information for form
        """
        model = Appointment
        date = forms.DateField()
        start_time = forms.TimeField()
        end_time = forms.TimeField()
        fields = ['date', 'start_time', 'end_time', 'description', 'recurring', 'weeks']

    def __init__(self, *args, **kwargs):
        """
        Initializes block off form information
        :param args: arguments
        :param kwargs: kwarguments
        """
        user = kwargs.pop('user', None)
        super(BlockOffForm, self).__init__(*args, **kwargs)
        self.fields['description'] = forms.CharField(required=False)
        self.fields['description'].widget.attrs = {'class': 'form-control'}
        self.fields['date'].widget.attrs = {'class': 'form-control'}
        self.fields['start_time'].widget.attrs = {'class': 'form-control'}
        self.fields['end_time'].widget.attrs = {'class': 'form-control'}
        self.fields['patient'] = forms.ModelChoiceField(required=False, widget=forms.HiddenInput(), initial=None,
                                                        queryset=Patient.objects.filter(
                                                            doctor=Doctor.objects.filter(user=user)[0]))
        self.fields['recurring'] = forms.BooleanField(required=False)
        self.fields['weeks'] = forms.IntegerField(required=False)
        self.fields['weeks'].widget.attrs = {'class': 'form-control'}


class TransferForm(forms.ModelForm):
    """
    Form for transferring patients
    """
    class Meta:
        """
        Patient model information for form
        """
        model = Patient
        transfer_to = forms.ModelChoiceField(queryset=Hospital.objects.all().order_by('-name'), required=False)
        fields = ['transfer_to', 'admitted_to']

    def __init__(self, *args, **kwargs):
        """
        Initializes transfer form information
        :param args: arguments
        :param kwargs: kwarguments
        """
        user = kwargs.pop('user', None)
        super(TransferForm, self).__init__(*args, **kwargs)

        if user and (len(Doctor.objects.filter(user=user)) != 0):
            self.fields['transfer_to'].widget.attrs = {'class': 'form-control'}
        if user and (len(Hospital_Admin.objects.filter(user=user)) != 0):
            self.fields['transfer_to'].widget.attrs = {'class': 'form-control'}
