
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


# Register your models here.

from .models import RegistrationType, WorkshopPricing, \
                    Participant, ParticipantRegistration, \
                    AimerMember

#from .workshop_pricing_admin_forms import WorkshopPricingForm  # Import the form

#class WorkshopPricingAdmin(admin.ModelAdmin):
#    form = WorkshopPricingForm

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "mobile_number", "designation", "department", "institute")
    search_fields = ("name", "email", "mobile_number", "designation", "department", "institute")

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(RegistrationType)
#admin.site.register(Participant)
#admin.site.register(WorkshopPricing, WorkshopPricingAdmin)
admin.site.register(WorkshopPricing)
admin.site.register(ParticipantRegistration)
admin.site.register(AimerMember)





