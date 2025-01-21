from django import forms
from .models import Participant, RegistrationType

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = [
                    'registration_type', 
                    'name', 
                    'email', 
                    'mobile_number',
                    
                    ]



