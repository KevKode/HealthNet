"""
file: admin_control.py
description: provides administrator-only views
"""

from django.views.generic import CreateView

from ..views import CreateLogItem
from ..forms import HospitalForm
from ..models import Hospital
from ..utils import get_user_type


class CreateHospital(CreateView):
    """
    View for Hospital Creation
    """
    form_class = HospitalForm
    model = Hospital
    template_name = 'HealthApps/create_hospital.html'
    success_url = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Updates form context data to include the request's user
        :return: updated context data
        """
        context = super(CreateView, self).get_context_data(**kwargs)
        context['user_type'] = get_user_type(self.request.user)
        return context

    def form_valid(self, form):
        """
        Overrides form_valid to create log item
        :param form: the specified form
        :return: the validity of the form
        """
        hospital = form.save(commit=False)
        CreateLogItem.li_hospital_create(self.request.user, hospital)
        return super(CreateHospital, self).form_valid(form)

