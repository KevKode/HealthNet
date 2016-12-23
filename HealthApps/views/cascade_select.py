"""
file: cascade_select.py
description: provides functions for cascading selects
"""

from django.http import JsonResponse
from ..models import Doctor


def hospital_to_doctor(request):
    """
    Gets all doctors associated with given hospital
    :param request: used to determine specified hospital
    :return: JSON response of doctors
    """
    hospital = request.GET.get('hospital')
    print(hospital)
    ret = []
    if hospital:
        for doctor in Doctor.objects.filter(hospitals__id__in=hospital):
            if doctor.cur_patients < doctor.max_patients:
                ret.append(dict(id=doctor.id, value=str(doctor)))
    return JsonResponse(ret, safe=False)
