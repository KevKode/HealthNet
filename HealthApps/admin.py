"""
file: admin.py
description: registers models for viewing in admin panel
"""


from django.contrib import admin

from .models import *


# username: admin
# password: djingledjango

admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(LogItem)
admin.site.register(Hospital)
admin.site.register(Hospital_Admin)
admin.site.register(EMR_Entry)
