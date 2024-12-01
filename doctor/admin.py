from django.contrib import admin
from .models import Specialty,Doctor,DoctorAvailability

# Register your models here.
admin.site.register(Specialty)
admin.site.register(Doctor)
admin.site.register(DoctorAvailability)