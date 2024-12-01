from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import login, logout

from patient.models import Patient, Appointment
from .models import Doctor, Specialty, DoctorAvailability
from datetime import datetime, date

# @login_required
# def book_appointment(request):
#     """
#     View to book an appointment
#     """
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
    


# doctor login and dashboard


from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# Custom Login View for Doctor
class DoctorLoginView(LoginView):
    template_name = 'doctor/login.html'

    def form_valid(self, form):
        user = form.get_user()
        # Check if the user is a doctor
        if hasattr(user, 'doctor'):
            login(self.request, user)
            return redirect('doctor_dashboard')  # Redirect to doctor's dashboard
        else:
            # If the user is not a doctor, log them out and show an error message
            return redirect('doctor_login')  # Or show an error message
        
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Doctor, DoctorAvailability
from patient.models import Appointment

@login_required
def doctor_dashboard(request):
    """
    Doctor dashboard view showing upcoming and past appointments.
    Past appointments include Completed and Cancelled statuses.
    """
    doctor = request.user.doctor  # Assuming the doctor is linked to the user via a OneToOneField
    
    # Get upcoming appointments (appointments that are in the future and are scheduled)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=timezone.now(),
        status='SCHEDULED'
    )
    
    # Get past appointments (appointments that are already completed or cancelled)
    past_appointments = Appointment.objects.filter(
        doctor=doctor,
        status__in=['COMPLETED', 'CANCELLED']
    )

    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    }
    return render(request, 'doctor/dashboard.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from patient.models import Patient

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def manage_appointment(request, appointment_id):
    """
    View to manage (cancel or complete) an appointment.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)

    if request.method == 'POST':
        action = request.POST.get('action')  # Action could be "cancel" or "complete"
        
        if action == 'cancel':
            appointment.status = 'CANCELLED'
            appointment.save()
            messages.success(request, 'Appointment cancelled successfully!')
        
        elif action == 'complete':
            appointment.status = 'COMPLETED'
            appointment.save()
            messages.success(request, 'Appointment marked as completed!')
        
        return redirect('doctor_dashboard')  # Redirect to the dashboard after the action

    return render(request, 'doctor/manage_appointment.html', {'appointment': appointment})

@login_required
def add_availability(request):
    """
    View to add availability slots for the doctor.
    """
    doctor = get_object_or_404(Doctor, user=request.user)
    
    if request.method == 'POST':
        try:
            # Get form data
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            
            # Check if the start_time is before the end_time
            if datetime.strptime(start_time, '%H:%M') >= datetime.strptime(end_time, '%H:%M'):
                messages.error(request, "End time must be after start time.")
                return redirect('doctor_dashboard')
            
            # Convert the date and time to appropriate types
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()

            # Create new availability slot
            availability_slot = DoctorAvailability.objects.create(
                doctor=doctor,
                date=date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj
            )
            messages.success(request, 'Availability slot added successfully!')
            return redirect('doctor_dashboard')
        
        except Exception as e:
            messages.error(request, f"Error adding availability: {str(e)}")
            return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')
@login_required
def update_availability(request, availability_id):
    """
    View to update availability slot for the doctor.
    """
    availability_slot = get_object_or_404(DoctorAvailability, id=availability_id)
    
    if request.method == 'POST':
        try:
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            
            if datetime.strptime(start_time, '%H:%M') >= datetime.strptime(end_time, '%H:%M'):
                messages.error(request, "End time must be after start time.")
                return redirect('doctor_dashboard')
            
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()

            # Update the availability slot
            availability_slot.date = date_obj
            availability_slot.start_time = start_time_obj
            availability_slot.end_time = end_time_obj
            availability_slot.save()

            messages.success(request, 'Availability slot updated successfully!')
            return redirect('doctor_dashboard')
        
        except Exception as e:
            messages.error(request, f"Error updating availability: {str(e)}")
            return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')

@login_required
def delete_availability(request, availability_id):
    """
    View to delete availability slot for the doctor.
    """
    availability_slot = get_object_or_404(DoctorAvailability, id=availability_id)
    availability_slot.delete()
    messages.success(request, 'Availability slot deleted successfully!')
    return redirect('doctor_dashboard')

def Doctor_logout_view(request):
    """
    Standard logout view with message and redirect
    """
    # Log out the user
    logout(request)
    
    # Add a success message
    messages.success(request, 'You have been successfully logged out.')
    
    # Redirect to login page or home page
    return redirect('doctor_login')


def Homepage(request):
    return render(request,'Home.html')