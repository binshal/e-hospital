from . import views
from django.urls import path



urlpatterns = [
    path('patient-register',views.PatientRegistrationView.as_view(),name='patient_register'),
    path('login/',views.PatientLoginView.as_view(),name='patient_login'),
    path('logout/', views.logout_view, name='patient_logout'),
    
    #Dashboard urls
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('appointments/', views.appointment_history, name='appointment_history'),
    
    #Health resources
    path('health-resources/', views.health_resources_list, name='health_resources_list'),
    path('health-resources/<int:resource_id>/', views.health_resource_detail, name='health_resource_detail'),
    path('health-resources/category/', views.filter_resources_by_category, name='filter_resources_by_category'),

    # Prescription
    path('prescribe/<int:appointment_id>/', views.create_prescription, name='create_prescription'),
    path('prescription-list/', views.prescriptions_list, name='prescription_list'),

    #billing
    # path('billing/',views.billing_details, name='billing_details'),
    # path('booking/',views.book_appointment, name='book-appointment'),
    # path('doctors/by-specialty/', views.get_doctors_by_specialty, name='doctors_by_specialty'), -------------------
    # path('doctors/availability/', views.get_doctor_availability, name='doctor_availability'),
    # path('update-billing-status/',views.update_billing_status, name='update_billing_status'),
    
    # path('create-billing-status/', views.create_payment_intent, name='update_billing_status'),
    # path('create-billing/', views.create_stripe_payment_intent, name='update_billing_status'),
    path('billing/', views.billing_details, name='billing_details'),
    path('billing/process-payment/', views.process_payment, name='process_payment'),
    path('billing/payment-success/', views.payment_success, name='payment_success'),
    path('billing/payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),

      # URL to load the booking appointment page
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    
    # API to fetch doctors based on selected specialty
    path('get-doctors-by-specialty/', views.get_doctors_by_specialty, name='get_doctors_by_specialty'),
    
    # API to fetch available time slots based on selected doctor and date
    path('get-available-slots/', views.get_available_slots, name='get_available_slots'),
    path('doctors/by-specialty/', views.get_doctors_by_specialty, name='get_doctors_by_specialty'),
    path('doctors/availability/', views.get_doctor_availability, name='get_doctor_availability'),

    
    # You can also add a success page for when the appointment is successfully booked
    # path('appointment-success/', views.appointment_success, name='appointment_success'),
    
    
]