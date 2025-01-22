from django import forms
from .models import Participant, RegistrationType

"""
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
                    'registration_type', 
                    'name', 
                    'email', 
                    'mobile_number',
                    
                    ]
"""

class RegistrationForm(forms.Form):
    registration_type = forms.ModelChoiceField(queryset=RegistrationType.objects.all())
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    mobile_number = forms.CharField(max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        print("Inside registration app - forms.py - cleaned_data\n",cleaned_data)
        registration_type = cleaned_data.get("registration_type")
        print("Inside registration app forms.py - registration_type\n", registration_type)
        # Check if participant with the same email already exists (for AIMER registration)
        if registration_type.name == "AIMER" and \
                                    Participant.objects.filter(email=cleaned_data["email"]).exists():
            raise forms.ValidationError("You are already registered as an AIMER member. \
                                        Please use a different email for workshop registration.")
        return cleaned_data

