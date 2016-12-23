"""
file: userauth.py
description: views and functions for logging in / out
"""

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from ..forms import LoginForm


def login(request):
    """
    View for login
    :param request: POST request
    :return: redirect or rendered login template
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/calView')
    else:
        return render(request, '/login.html', {'form': LoginForm})

@login_required
def restricted(request):
    """
    Returns un-restricted message
    :param request: request
    :return: response
    """
    return HttpResponse("Since you're logged in, you can see this text!")


@login_required
def logout(request):
    """
    Logs out
    :param request: request
    :return: redirect
    """
    logout(request)
    return HttpResponseRedirect('/index.html')
