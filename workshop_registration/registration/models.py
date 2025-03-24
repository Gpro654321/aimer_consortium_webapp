# Create your models here.

from django.db import models
from django.db import models, IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
#from .registration_types import REGISTRATION_TYPES
from datetime import date
from .location_models import State, District
from .choices import GENDER_CHOICES

'''
class Participant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20)
    designation = models.CharField(max_length=255, null=True, blank=True, 
                                   help_text="Participant's designation (e.g., Professor, Researcher)")
    department = models.CharField(max_length=255, null=True, blank=True, 
                                  help_text="Department name")
    institute = models.CharField(max_length=255, null=True, blank=True, 
                                 help_text="Institute or organization name")
    
    # need to add Gender, District and State

    def __str__(self):
        return f"{self.name} ({self.designation if self.designation else 'No Designation'})"
'''




class Participant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20)
    designation = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    institute = models.CharField(max_length=255, null=True, blank=True)
    
    # Gender field using separate choices
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    # Link to State & District models
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["name"]  # Sort participants alphabetically

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()}), {self.district}, {self.state}"


class AimerMember(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    is_active_member = models.BooleanField(default=True)
    joined_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant.name} {self.is_active_member} (AIMER Member)"

class RegistrationType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        if self.name == "AIMER":
            return self.name + " Consortium Annual Membership"
        else:
            return self.name

class WorkshopPricing(models.Model):
    workshop_name = models.ForeignKey(RegistrationType, on_delete=models.CASCADE,related_name='workshop_pricings')
    early_bird_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    aimer_member_price = models.DecimalField(
                                        max_digits=10, decimal_places=2, null=True, 
                                        blank=True, 
                                        help_text="Price for AIMER members (leave blank if not applicable)"
                                        )
    # cut_off_date is the date on which early bird registrations stop and normal prices resume
    cut_off_date = models.DateField(null=True, blank=True)
    workshop_start_date = models.DateField(
                                        null=True,
                                        blank=False,
                                        help_text="Date on which workshop starts"
                                           )
    workshop_end_date = models.DateField(
                                        null=True,
                                        blank=False,
                                        help_text="Date on which workshop ends"
                                        )
    is_alive = models.BooleanField(
                                    default=False
                                        )
    
    # this field is introduced so that, AIMER membership can be controlled
    # if open_for_all is True anybody can register
    # if it is false, I am going implement a logic if the particular mail id is already found in our\
    # database
    is_open_for_all = models.BooleanField(
                                    default=True
                                            )
    
    # ✅ WhatsApp Group Link (Used in email, NOT shown in registration form)
    whatsapp_group_link = models.URLField(
        max_length=500, 
        null=True, 
        blank=True, 
        help_text="WhatsApp group link for participants (Will be sent via email, not shown in form)."
    )

    # ✅ Brochure Link (Shown in workshop details in registration form)
    brochure_link = models.URLField(
        max_length=500, 
        null=True, 
        blank=True, 
        help_text="Link to the workshop brochure (This will be displayed in the registration form)."
    )


    def __str__(self):
        return f"{self.workshop_name.name} Pricing"

class ParticipantRegistration(models.Model):  # New model for registration details
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    registration_type = models.ForeignKey(RegistrationType, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=50, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    '''
    class Meta:
        unique_together = ('participant', 'registration_type') 
    '''   
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['participant', 'registration_type'],
                condition=Q(payment_status=True),  # Ensures uniqueness only when payment is successful
                name='unique_paid_registration'
            )
        ]


    def __str__(self):
        return f"{self.participant.name} - {self.registration_type.name}"

    
    def save(self, *args, **kwargs):
        try:
            print("Inside /save/ParticipantRegistration/Model")
            super().save(*args, **kwargs) 
        except IntegrityError:
            raise ValidationError("Participant is already registered for this workshop.")
        



class RazorpayPayment(models.Model):
    class Meta:
        verbose_name_plural = "Razorpay Payments"
