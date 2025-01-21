# Create your models here.

from django.db import models
#from .registration_types import REGISTRATION_TYPES
from datetime import date

class RegistrationType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class WorkshopPricing(models.Model):
    workshop_name = models.ForeignKey(RegistrationType, on_delete=models.CASCADE)
    early_bird_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    aimer_member_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price for AIMER members (leave blank if not applicable)") #Added this line
    cut_off_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.workshop_name.name} Pricing"

class Participant(models.Model):
    registration_type = models.ForeignKey(RegistrationType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    is_aimer_member = models.BooleanField(default=False)  # Add this field
    razorpay_order_id = models.CharField(max_length=50, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name