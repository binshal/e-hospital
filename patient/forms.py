from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Patient

class PatientRegistrationForm(UserCreationForm):
    """
    Extended user creation form for patient registration
    """
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        """
        Override save method to set email
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
       
from django import forms
from .models import Prescription

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medications', 'instructions']  # Only the fields needed for prescription
        widgets = {
            'medications': forms.Textarea(attrs={'placeholder': 'Enter prescribed medications', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'placeholder': 'Enter instructions for the patient', 'rows': 3}),
        }