from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.views.generic.edit import FormView
from django.utils import timezone
from django.http import JsonResponse


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Patient, Appointment, Billing, HealthEducationResource,Prescription

from .models import Patient, Appointment, Billing, HealthEducationResource
from .forms import PatientRegistrationForm

class PatientRegistrationView(CreateView):
    """
    View for patient registration that creates both User and Patient instances
    """
    template_name = 'patient/register.html'
    form_class = PatientRegistrationForm
    success_url = reverse_lazy('patient_dashboard')

    def form_valid(self, form):
        """
        Create both User and Patient instances when form is valid
        """
        response = super().form_valid(form)
        user = form.save()
        
        # Create Patient instance
        patient = Patient.objects.create(
            user=user,
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            date_of_birth=form.cleaned_data.get('date_of_birth'),
            phone_number=form.cleaned_data.get('phone_number'),
            email=user.email
        )
        
        # Log the user in
        login(self.request, user)
        messages.success(self.request, 'Registration successful!')
        return response
    
# class PatientLoginView(CreateView):
#     """
#     Custom login view for patients
#     """
#     template_name = 'patient/login.html'
#     form_class = AuthenticationForm
#     success_url = reverse_lazy('patient_dashboard')

#     def form_valid(self, form):
#         """
#         Log in the user
#         """
#         login(self.request, form.get_user())
#         messages.success(self.request, 'Login successful!')
#         return super().form_valid(form)


class PatientLoginView(FormView):
    """
    Custom login view for patients
    """
    template_name = 'patient/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('patient_dashboard')

    def form_valid(self, form):
        """
        Log in the user and redirect to success URL
        """
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, 'Login successful!')
        return super().form_valid(form)
    
# Dashboard view

@login_required
def patient_dashboard(request):
    """
    Dashboard view for patients to see their personal information, 
    upcoming appointments, billing, and health resources.
    """
    try:
        # Get the patient associated with the logged-in user
        patient = Patient.objects.get(user=request.user)
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            patient=patient, 
            status='SCHEDULED'
        ).order_by('appointment_date')
        
        # Get billing information
        billing_history = Billing.objects.all()
        
        # Get health education resources
        health_resources = HealthEducationResource.objects.all()

        #prescription
        prescriptions = Prescription.objects.all()
        
        context = {
            'prescriptions' : prescriptions,
            'patient': patient,
            'upcoming_appointments': upcoming_appointments,
            'billing_history': billing_history,
            'health_resources': health_resources,
        }
        
        return render(request, 'patient/dashboard.html', context)
    
    except Patient.DoesNotExist:
        # Handle case where no patient profile exists for the user
        return render(request, 'patient/dashboard.html', {
            'error': 'No patient profile found.'
        })

@login_required
def appointment_history(request):
    """
    View to show patient's full appointment history
    """
    try:
        patient = Patient.objects.get(user=request.user)
        all_appointments = Appointment.objects.filter(patient=patient)
        
        
        context = {
            'appointments': all_appointments,
        }
        
        return render(request, 'patient/appointment_history.html', context)
    
    except Patient.DoesNotExist:
        return render(request, 'patient/appointment_history.html', {
            'error': 'No patient profile found.'
        })

# @login_required
# def billing_details(request):
#     """
#     View to show patient's detailed billing information
#     """
#     try:
#         patient = Patient.objects.get(user=request.user)
#         billing_history = Billing.objects.filter(patient=patient)
        
#         context = {
#             'billing_history': billing_history,
#             'total_unpaid': sum(bill.amount for bill in billing_history if bill.status == 'UNPAID'),
#         }
        
#         return render(request, 'patient/billing_details.html', context)
    
#     except Patient.DoesNotExist:
#         return render(request, 'patient/billing_details.html', {
#             'error': 'No patient profile found.'
#         })

#Health Education resource   
@login_required
def health_resources_list(request):
    """
    View to list all health education resources
    """
    # Fetch all health education resources, optionally can add filtering
    resources = HealthEducationResource.objects.all()
    
    context = {
        'resources': resources,
        'categories': set(resources.values_list('category', flat=True).distinct())
    }
    
    return render(request, 'patient/health_resources.html', context)

@login_required
def health_resource_detail(request, resource_id):
    """
    View to show detailed information about a specific health resource
    """
    # Get the specific resource or return 404 if not found
    resource = get_object_or_404(HealthEducationResource, id=resource_id)
    
    # Optional: You could add related resources logic here
    related_resources = HealthEducationResource.objects.filter(
        category=resource.category
    ).exclude(id=resource.id)[:3]
    
    context = {
        'resource': resource,
        'related_resources': related_resources
    }
    
    return render(request, 'patient/health_resource_detail.html', context)

@login_required
def filter_resources_by_category(request):
    """
    View to filter health resources by category
    """
    category = request.GET.get('category')
    
    if category:
        resources = HealthEducationResource.objects.filter(category=category)
    else:
        resources = HealthEducationResource.objects.all()
    
    context = {
        'resources': resources,
        'categories': set(HealthEducationResource.objects.values_list('category', flat=True).distinct()),
        'selected_category': category
    }
    
    return render(request, 'patient/health_resources.html', context)

#Logout view
def logout_view(request):
    """
    Standard logout view with message and redirect
    """
    # Log out the user
    logout(request)
    
    # Add a success message
    messages.success(request, 'You have been successfully logged out.')
    
    # Redirect to login page or home page
    return redirect('patient_login')

# Prescription

def prescriptions_list(request):
    prescriptions = Prescription.objects.all()  # You can filter by doctor or patient if needed
    return render(request, 'patient/prescriptions_list.html', {'prescriptions': prescriptions})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Prescription
from .forms import PrescriptionForm
from doctor.models import Doctor

def create_prescription(request, appointment_id):
    # Get the appointment object based on the appointment_id
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Ensure that the doctor accessing this view is the one associated with the appointment
    if request.user != appointment.doctor.user:
        return redirect('doctor_dashboard')  # Redirect if the doctor is not associated with the appointment

    # Process the form submission
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            # Create a new prescription associated with this appointment
            prescription = form.save(commit=False)
            prescription.doctor = appointment.doctor  # Associate doctor with the prescription
            prescription.patient = appointment.patient  # Associate patient with the prescription
            prescription.appointment = appointment  # Associate appointment with the prescription
            prescription.save()
            return redirect('doctor_dashboard')  # Redirect to the doctor dashboard after saving
    else:
        # Create the form to be displayed
        form = PrescriptionForm()

    return render(request, 'patient/create_prescription.html', {'form': form, 'appointment': appointment})


# after billing 
#-----------------------------------------------------------------------------------------------------------------------------

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from .models import Appointment, Patient, Billing
from django.db.models import F
from doctor.models import  DoctorAvailability,Specialty
from django.utils.timezone import make_aware

# @login_required
# def book_appointment(request):
#     """
#     View to book an appointment
#     """
#     appointment = None  # Initialize appointment to None

#     if request.method == 'POST':
#         try:
#             # Get form data
#             availability_id = request.POST.get('availability_slot')
            
#             # Fetch the availability slot
#             availability_slot = get_object_or_404(DoctorAvailability, 
#                 id=availability_id, 
#                 status='AVAILABLE'
#             )
            
#             # Get the patient
#             patient = Patient.objects.get(user=request.user)
            
#             # Use transaction to ensure atomic booking
#             with transaction.atomic():
#                 # Create appointment
#                 appointment = Appointment.objects.create(
#                     patient=patient,
#                     doctor=availability_slot.doctor,
#                     appointment_date=timezone.make_aware(datetime.combine(
#                         availability_slot.date, 
#                         availability_slot.start_time
#                     )),
#                     preferred_time=availability_slot.start_time,
#                     status='SCHEDULED'
#                 )
#                  # Create corresponding billing entry
#                 Billing.objects.create(
#                     patient=patient,
#                     amount=appointment.doctor.consultation_fee,
#                     date=timezone.now(),
#                     status='UNPAID',
#                     insurance_info=f"Consultation with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}"
#                 )
                
#                 # Update availability slot
#                 availability_slot.status = 'BOOKED'
#                 availability_slot.save()
                
#                 messages.success(request, 'Appointment booked successfully!')
#                 return redirect('appointment_history')
        
#         except Patient.DoesNotExist:
#             messages.error(request, 'Patient profile not found. Please complete your profile.')
#             return redirect('create_patient_profile')
        
#         except Exception as e:
#             messages.error(request, f'An error occurred: {str(e)}')
#             return redirect('book_appointment')
    
#     # GET request - show booking form
#     specialties = Specialty.objects.all()
#     doctors = Doctor.objects.filter(is_active=True)
    
#     context = {
#         'appointment': appointment,  # If appointment is not created, this will be None
#         'specialties': specialties,
#         'doctors': doctors
#     }
#     return render(request, 'doctor/book_appointment.html', context)

# def get_doctors_by_specialty(request):
#     """
#     AJAX view to get unique doctors for a specific specialty
#     """
#     specialty_id = request.GET.get('specialty_id')
    
#     try:
#         # Find doctors in the specified specialty
#         doctors = Doctor.objects.filter(
#             specialty_id=specialty_id, 
#             is_active=True
#         ).distinct()
        
#         # Create doctor list with unique doctors
#         doctor_list = [
#             {
#                 'id': doctor.id,
#                 'name': f"Dr. {doctor.first_name} {doctor.last_name}"
#             } for doctor in doctors
#         ]
        
#         return JsonResponse({'doctors': doctor_list})
    
#     except Exception as e:
#         print(f"Error in get_doctors_by_specialty: {str(e)}")
#         return JsonResponse({'error': str(e)}, status=400)
    
# from datetime import date

# @login_required
# def get_doctor_availability(request):
#     """
#     AJAX view to get doctor's available slots
#     Improved to handle date parsing and slot availability
#     """
#     doctor_id = request.GET.get('doctor_id')
#     date_str = request.GET.get('date')
    
#     print(f"Received doctor_id: {doctor_id}, date: {date_str}")
    
#     try:
#         # Convert date string to date object
#         selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
#         # Check if selected date is in the future
#         if selected_date < date.today():
#             return JsonResponse({'error': 'Please select a future date'}, status=400)
        
#         # Find available slots for the doctor on the specified date
#         available_slots = DoctorAvailability.objects.filter(
#             doctor_id=doctor_id,
#             date=selected_date,
#             status='AVAILABLE'
#         ).order_by('start_time')
        
#         print(f"Found {available_slots.count()} available slots")
        
#         slots = [
#             {
#                 'id': slot.id,
#                 'start_time': slot.start_time.strftime('%I:%M %p'),
#                 'end_time': slot.end_time.strftime('%I:%M %p')
#             } for slot in available_slots
#         ]
        
#         return JsonResponse({'slots': slots})
    
#     except ValueError:
#         print("Invalid date format")
#         return JsonResponse({'error': 'Invalid date format'}, status=400)
#     except Exception as e:
#         print(f"Error fetching availability: {str(e)}")
#         return JsonResponse({'error': str(e)}, status=400)

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def billing_details(request):
    try:
        patient = Patient.objects.get(user=request.user)
        
        # Fetch unpaid bills
        billing_history = Billing.objects.filter(patient=patient, status='UNPAID')
        
        # Calculate total unpaid amount
        total_unpaid = sum(bill.amount for bill in billing_history)
        
        # Stripe setup
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        
        context = {
            'billing_history': billing_history,
            'total_unpaid': total_unpaid,
            'stripe_public_key': stripe_public_key,
        }
        
        return render(request, 'patient/billing_details.html', context)
    
    except Patient.DoesNotExist:
        messages.error(request, 'No patient profile found.')
        return redirect('patient_profile_creation')

@login_required
def process_payment(request):
    if request.method == 'POST':
        try:
            # Set up Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Get the patient and their unpaid bills
            patient = Patient.objects.get(user=request.user)
            billing_history = Billing.objects.filter(patient=patient, status='UNPAID')
            total_unpaid = sum(bill.amount for bill in billing_history)
            
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(total_unpaid * 100),  # Convert to cents
                        'product_data': {
                            'name': f'Medical Bill Payment for {patient.first_name} {patient.last_name}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/billing/payment-success/'),
                cancel_url=request.build_absolute_uri('/billing/payment-cancelled/'),
            )
            
            # Redirect to Stripe Checkout
            return redirect(checkout_session.url)
        
        except Patient.DoesNotExist:
            messages.error(request, 'Patient not found.')
            return redirect('billing_details')
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('billing_details')
    
    return redirect('billing_details')

def payment_success(request):
    # Mark bills as paid
    patient = Patient.objects.get(user=request.user)
    unpaid_bills = Billing.objects.filter(patient=patient, status='UNPAID')
    
    for bill in unpaid_bills:
        bill.status = 'PAID'
        bill.save()
    
    messages.success(request, 'Payment successful! All outstanding bills have been paid.')
    return redirect('billing_details')

def payment_cancelled(request):
    messages.warning(request, 'Payment was cancelled.')
    return redirect('billing_details')

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from datetime import datetime

import logging

@login_required
def book_appointment(request):
    specialties = Specialty.objects.all()
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('appointment_date')
        time_slot_id = request.POST.get('time_slot')

        logging.debug(f"Doctor ID: {doctor_id}, Date: {date}, Time Slot ID: {time_slot_id}")

        # Check if the date is missing
        if not date:
            logging.error("Appointment date is missing in the form submission.")
            return JsonResponse({"error": "Appointment date is required"}, status=400)

        try:
            # Get the doctor object
            doctor = Doctor.objects.get(id=doctor_id)

            # Log the received date
            logging.debug(f"Received appointment date: {date}")

            # Try to parse the date
            parsed_date = datetime.strptime(date, '%Y-%m-%d').date()

            # Attempt to get the time slot
            time_slot = DoctorAvailability.objects.filter(
                id=time_slot_id, doctor=doctor, date=parsed_date, status='AVAILABLE'
            ).first()

            if not time_slot:
                logging.error(f"Time Slot with ID {time_slot_id} not found or is not available.")
                return JsonResponse({"error": "Selected time slot is unavailable or invalid"}, status=404)

        except Doctor.DoesNotExist:
            logging.error(f"Doctor with ID {doctor_id} does not exist.")
            return JsonResponse({"error": "Doctor not found"}, status=404)
        except ValueError as e:
            # This will catch invalid date format errors (when strptime fails)
            logging.error(f"Error parsing date: {e}")
            return JsonResponse({"error": "Invalid date format"}, status=400)
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)

        # If the time slot is valid, create the appointment
        appointment = Appointment(
            patient=request.user.patient,
            doctor=doctor,
            appointment_date=datetime.combine(parsed_date, time_slot.start_time),
            preferred_time=time_slot.start_time,
        )
        # appointment = Appointment(
        #     patient=request.user.patient,  # Assuming the logged-in user has a related patient object
        #     doctor=doctor,
        #     appointment_date=parsed_date,
        #     preferred_time=time_slot.start_time,
        # )
        appointment.save()

        patient = Patient.objects.get(user=request.user)

        Billing.objects.create(
                    patient=patient,
                    amount=appointment.doctor.consultation_fee,
                    date=timezone.now(),
                    status='UNPAID',
                    insurance_info=f"Consultation with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}"
                )

        logging.info(f"Appointment booked successfully with {doctor.first_name} {doctor.last_name} for {parsed_date} at {time_slot.start_time}")

        return redirect('appointment_history')  # Redirect to a success page or wherever you want after booking

    return render(request, 'patient/book_appointment.html', {'specialties': specialties})





def get_available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date = request.GET.get('date')
    doctor = Doctor.objects.get(id=doctor_id)
    available_slots = DoctorAvailability.objects.filter(doctor=doctor, date=date, status='AVAILABLE')
    slots_data = [
        {"id": slot.id, "start_time": slot.start_time.strftime('%H:%M'), "end_time": slot.end_time.strftime('%H:%M')}
        for slot in available_slots
    ]
    return JsonResponse({'slots': slots_data})
def get_doctors_by_specialty(request):
    specialty_id = request.GET.get('specialty_id')
    if specialty_id:
        try:
            specialty = Specialty.objects.get(id=specialty_id)
            doctors = Doctor.objects.filter(specialty=specialty, is_active=True)
            doctor_list = [{"id": doctor.id, "name": f"Dr. {doctor.first_name} {doctor.last_name}"} for doctor in doctors]
            return JsonResponse({"doctors": doctor_list})
        except Specialty.DoesNotExist:
            return JsonResponse({"error": "Specialty not found"}, status=404)
    return JsonResponse({"error": "Specialty ID not provided"}, status=400)


def get_doctor_availability(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({"error": "Doctor ID and date must be provided"}, status=400)

    try:
        # Convert date string to a date object
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get the doctor by ID
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Get available time slots for the selected doctor and date
        available_slots = DoctorAvailability.objects.filter(
            doctor=doctor,
            date=selected_date,
            status='AVAILABLE'
        ).order_by('start_time')
        
        # Return the available slots in JSON format
        slots = [
            {
                'id': slot.id,
                'start_time': slot.start_time.strftime('%I:%M %p'),
                'end_time': slot.end_time.strftime('%I:%M %p')
            } for slot in available_slots
        ]

        return JsonResponse({'slots': slots})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
