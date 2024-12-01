from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',views.Homepage,name='home'),
    # Appointment Booking
    # path('book-appointment/',views.book_appointment, name='book_appointment'),
    # path('doctors/by-specialty/', views.get_doctors_by_specialty, name='doctors_by_specialty'),
    # path('doctors/availability/', views.get_doctor_availability, name='doctor_availability'),

    #login
    path('doctor-login/', views.DoctorLoginView.as_view(), name='doctor_login'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('add_availability/', views.add_availability, name='add_availability'),
    path('update_availability/<int:availability_id>/', views.update_availability, name='update_availability'),
    path('delete_availability/<int:availability_id>/', views.delete_availability, name='delete_availability'),
    path('doctor-logout/',views.Doctor_logout_view, name='doctor_logout'),
    path('appointment/manage/<int:appointment_id>/', views.manage_appointment, name='manage_appointment'),
    
]