from django.db import models
from django.contrib.auth.models import User
from doctor.models import Doctor
from django.conf import settings



class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Demographic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    # Contact Information
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    # Medical History
    medical_history = models.TextField(blank=True, help_text='Previous medical conditions and treatments')
    medications = models.TextField(blank=True, help_text='Current medications')
    allergies = models.TextField(blank=True, help_text='Known allergies')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Appointment(models.Model):
    """
    Appointment model for booking and managing patient appointments
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateTimeField()
    preferred_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('SCHEDULED', 'Scheduled'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed')
    ], default='SCHEDULED')
    
    def __str__(self):
        # return f"Appointment for {self.patient.full_name} on {self.appointment_date}"
        return f"Appointment for {self.patient} on {self.appointment_date}"


class Billing(models.Model):
    """
    Billing model to manage patient billing and payments
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=[
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid')
    ], default='UNPAID')
    insurance_info = models.TextField(blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)

    # def create_stripe_payment_intent(self):
    #     """
    #     Create a Stripe Payment Intent for this billing record
    #     """
    #     import stripe
    #     stripe.api_key = settings.STRIPE_SECRET_KEY
        
    #     try:
    #         intent = stripe.PaymentIntent.create(
    #             amount=int(self.amount * 100),  # Convert to cents
    #             currency='usd',
    #             payment_method_types=['card'],
    #             metadata={'billing_id': self.id}
    #         )
    #         self.stripe_payment_intent = intent.id
    #         self.save()
    #         return intent.client_secret
    #     except Exception as e:
    #         # Log the error
    #         return None

    def __str__(self):
        # return f"Billing for {self.patient.full_name} - ${self.amount}"
        return f"Billing for {self.patient} - ${self.amount}"




class HealthEducationResource(models.Model):
    """
    Health education resources model
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    resource_url = models.URLField(blank=True)

    def __str__(self):
        return self.title
    
class Prescription(models.Model):
    """
    Prescription model for doctors to prescribe medications to patients.
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)  # ForeignKey to Doctor
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # ForeignKey to Patient (this app)
    medications = models.TextField(help_text="Medications prescribed")
    instructions = models.TextField(help_text="Instructions for the patient")
    created_at = models.DateTimeField(auto_now_add=True)  # When the prescription is created
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)  # ForeignKey to Appointment

    def __str__(self):
        return f"Prescription for {self.patient} by Dr. {self.doctor}"