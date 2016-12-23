"""
file: index.py
description: view for index
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..models import Hospital
from ..forms import LoginForm
from ..utils import get_user_type


def index(request):
    """
    Login on the index
    :param request:
    :return: renders the page
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/profile')
    else:
        form = LoginForm()

    user_type = get_user_type(request.user)
    hospitals = []
    for hos in Hospital.objects.all():
        hospitals.append(hos)

    return render(request, 'HealthApps/index.html', dict(form=form, user_type=user_type, hospitals=hospitals))
