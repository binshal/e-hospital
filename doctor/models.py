from django.db import models
from django.contrib.auth.models import User

class Specialty(models.Model):
    """
    Medical Specialties for doctors
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    """
    Doctor model with user association and professional details
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True)
    
    # Professional Information
    medical_license_number = models.CharField(max_length=50, unique=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Availability Management
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialty}"

class DoctorAvailability(models.Model):
    """
    Doctor's availability slots for appointments
    """
    SLOT_STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BOOKED', 'Booked'),
        ('COMPLETED', 'Completed')
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=SLOT_STATUS_CHOICES, default='AVAILABLE')
    
    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}-{self.end_time}"
    