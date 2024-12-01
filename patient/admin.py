from django.contrib import admin
from .models import Appointment,Billing

# Register your models here.
admin.site.register(Appointment)
admin.site.register(Billing)