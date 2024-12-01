from django import forms
from .models import Doctor
from django.utils import timezone
from patient.models import Appointment

class AppointmentForm(forms.ModelForm):
    """
    Form for creating a new appointment
    """
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True),
        required=True,
        label='Select Doctor'
    )
    
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=True,
        label='Appointment Date and Time'
    )
    
    preferred_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=False,
        label='Preferred Time (Optional)'
    )
    
    insurance_info = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Insurance Information (Optional)'
    )
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'preferred_time']
    
    def clean_appointment_date(self):
        """
        Validate appointment date
        """
        appointment_date = self.cleaned_data.get('appointment_date')
        
        # Check if appointment is in the future
        if appointment_date <= timezone.now():
            raise forms.ValidationError("Appointment must be scheduled in the future.")
        
        return appointment_date