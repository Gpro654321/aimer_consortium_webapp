
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db.models import Prefetch


# Register your models here.

from .models import RegistrationType, WorkshopPricing, \
                    Participant, ParticipantRegistration, \
                    AimerMember

from .location_models import District, State

#from .workshop_pricing_admin_forms import WorkshopPricingForm  # Import the form

#class WorkshopPricingAdmin(admin.ModelAdmin):
#    form = WorkshopPricingForm

class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "mobile_number", "designation", "department", "institute")
    search_fields = ("name", "email", "mobile_number", "designation", "department", "institute")

class ParticipantRegistrationAdmin(admin.ModelAdmin):
    list_display = ("get_participant_name", "registration_type", "razorpay_payment_id",
                     "payment_status", "amount_paid", "registered_at")
    #search_fields = ("get_participant_name", "registration_type", "payment_status", "amount_paid", "registered_at")
    search_fields = ("participant__name", "registration_type__name", "razorpay_payment_id")

    def get_participant_name(self, obj):
        return obj.participant.name  # Access the name from the related Participant model
    get_participant_name.admin_order_field = "participant__name"  # Enable sorting by name
    get_participant_name.short_description = "Participant Name"  # Display a user-friendly column name

'''
class AimerMemberAdmin(admin.ModelAdmin):
    list_display = ("get_participant_name",)
    search_fields = ("participant__name",)

    def get_participant_name(self, obj):
        return obj.participant.name  # Access the name from the related Participant model
    get_participant_name.admin_order_field = "participant__name"  # Enable sorting by name
    get_participant_name.short_description = "Participant Name"  # Display a user-friendly column name
'''

class AimerMemberAdmin(admin.ModelAdmin):
    list_display = ('get_participant_name', 'is_active_member', 'joined_at', 'previous_workshops')
    #search_fields = ("participant__name",)
    search_fields = ("participant__name", "participant__participantregistration__registration_type__name")

    def get_participant_name(self, obj):
        return obj.participant.name  # Access the name from the related Participant model

    def previous_workshops(self, obj):
        """
        Retrieves all workshops where the participant has successfully registered.
        """
        

        registrations = ParticipantRegistration.objects.filter(
            participant=obj.participant, 
            payment_status=True  # Only fetch successful payments
        ).exclude(registration_type__name="AIMER")  # Exclude AIMER workshop
        registrations = registrations.select_related('registration_type')

        if registrations.exists():
            return ", ".join([reg.registration_type.name for reg in registrations])
        return ""+"open"

    previous_workshops.short_description = "Previous Workshops"  # Column name in Django admin

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(RegistrationType)
#admin.site.register(Participant)
#admin.site.register(WorkshopPricing, WorkshopPricingAdmin)
admin.site.register(WorkshopPricing)
admin.site.register(ParticipantRegistration, ParticipantRegistrationAdmin)
admin.site.register(AimerMember, AimerMemberAdmin)

admin.site.register(District)
admin.site.register(State)





