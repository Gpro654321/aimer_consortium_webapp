from django import forms
from .models import Participant, RegistrationType
from .choices import GENDER_CHOICES  # Import choices from choices.py

from .location_models import State,District
from datetime import date

class RegistrationForm(forms.Form):
    today = date.today()

    registration_type = forms.ModelChoiceField(
        queryset=RegistrationType.objects.filter(
            workshop_pricings__is_alive=True,
            workshop_pricings__workshop_end_date__gte=today
        ).distinct().order_by('workshop_pricings__workshop_start_date'),
        label="Select Workshop"
    )

    name = forms.CharField(max_length=255, label="Full Name")
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label="Gender", required=True)
    email = forms.EmailField(label="Email")
    mobile_number = forms.CharField(max_length=20, label="Mobile Number")
    
    designation = forms.CharField(max_length=255, required=False, label="Designation")
    department = forms.CharField(max_length=255, required=False, label="Department")
    institute = forms.CharField(max_length=255, required=False, label="Institute/Organization")
    '''
    district = forms.CharField(max_length=255, label="District", 
                               widget=forms.TextInput(attrs={"class": "autocomplete"}))
    state = forms.CharField(max_length=255, label="State", 
                            widget=forms.TextInput(attrs={"class": "autocomplete"}))
    '''
    
    state = forms.ModelChoiceField(
                queryset=State.objects.all(), 
                label="State",
                empty_label="Select State"
                    )

    district = forms.ModelChoiceField(
                queryset=District.objects.all(), 
                label="District",
                empty_label="Select District"
                    )
    
    '''
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Participant.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email
    '''

    def clean(self):
        cleaned_data = super().clean()
        registration_type = cleaned_data.get("registration_type")

        print("Inside registration app forms.py - cleaned_data\n", cleaned_data)
        print("Inside registration app forms.py - registration_type\n", registration_type)

        return cleaned_data
