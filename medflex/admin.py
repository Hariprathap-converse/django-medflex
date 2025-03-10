from django.contrib import admin

from .models import Doctor, DoctorAvailability, LoginLogs

admin.site.register(LoginLogs)

admin.site.register(Doctor)

admin.site.register(DoctorAvailability)
