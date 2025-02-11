# Create your models here.

from django.db import models
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
#from .registration_types import REGISTRATION_TYPES
from datetime import date


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

    def __str__(self):
        return f"{self.name} ({self.designation if self.designation else 'No Designation'})"


class AimerMember(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    is_active_member = models.BooleanField(default=True)
    joined_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant.name} {self.is_active_member} (AIMER Member)"

class RegistrationType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
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

    class Meta:
        unique_together = ('participant', 'registration_type') 

    def __str__(self):
        return f"{self.participant.name} - {self.registration_type.name}"

    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs) 
        except IntegrityError:
            raise ValidationError("Participant is already registered for this workshop.")