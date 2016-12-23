"""
file: handle_csv.py
description: views for csv
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from ..utils import *


def handle_csv(request):
    """
    Handles the csv
    :param request:
    :return: renders the request
    """
    return render(request, 'HealthApps/handle_csv.html')


def import_csv(request, string):
    """
    Imports the csv
    :param request: the request
    :param string: the filename
    :return: redirects
    """
    import_data(string)
    return HttpResponseRedirect("/handleCSV")


def export_csv(request, string):
    """
    Exports the csv
    :param request: the request
    :param string: the filename
    :return: redirects
    """
    export_data(string)
    return HttpResponseRedirect("/handleCSV")
