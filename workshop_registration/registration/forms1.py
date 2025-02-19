from django import forms
from .models import Participant, RegistrationType
from datetime import date

"""
class RegistrationForm(forms.Form):
    today = date.today() 
    registration_type = forms.ModelChoiceField(
                            queryset = RegistrationType.objects.filter(
                                            workshop_pricings__is_alive=True,  # Filter by related WorkshopPricing model
                                            workshop_pricings__workshop_end_date__gte=today  # Filter by workshop end date
                                        ).distinct()  # Remove duplicates (optional)
                            )
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    mobile_number = forms.CharField(max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        print("Inside registration app - forms.py - cleaned_data\n",cleaned_data)
        registration_type = cleaned_data.get("registration_type")
        print("Inside registration app forms.py - registration_type\n", registration_type)
        # Check if participant with the same email already exists (for AIMER registration);
        '''
        if registration_type.name == "AIMER" and \
                                    Participant.objects.filter(email=cleaned_data["email"]).exists():
            raise forms.ValidationError("You are already registered as an AIMER member. \
                                        Please use a different email for workshop registration.")
        '''
        return cleaned_data
"""

class RegistrationForm(forms.Form):
    today = date.today() 

    registration_type = forms.ModelChoiceField(
        queryset=RegistrationType.objects.filter(
            workshop_pricings__is_alive=True,  
            workshop_pricings__workshop_end_date__gte=today  
        ).distinct(),  # Remove duplicates (optional)
        label="Select Workshop"
    )
    
    name = forms.CharField(max_length=255, label="Full Name")
    email = forms.EmailField(label="Email")
    mobile_number = forms.CharField(max_length=20, label="Mobile Number")
    designation = forms.CharField(max_length=255, required=False, label="Designation")
    department = forms.CharField(max_length=255, required=False, label="Department")
    institute = forms.CharField(max_length=255, required=False, label="Institute/Organization")

    def clean(self):
        cleaned_data = super().clean()
        print("Inside registration app - forms.py - cleaned_data\n", cleaned_data)

        registration_type = cleaned_data.get("registration_type")
        email = cleaned_data.get("email")

        print("Inside registration app forms.py - registration_type\n", registration_type)

        return cleaned_data


