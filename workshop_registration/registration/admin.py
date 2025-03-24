
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db.models import Prefetch


# admin.py
import os
import razorpay
from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.http import HttpResponse
from django.template.response import TemplateResponse
from datetime import datetime

# Register your models here.

from .models import RegistrationType, WorkshopPricing, \
                    Participant, ParticipantRegistration, \
                    AimerMember, RazorpayPayment

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





# Initialize Razorpay client
RAZORPAY_API_KEY = os.environ.get("key_id")
RAZORPAY_API_SECRET = os.environ.get("key_secret")
razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))


class RazorpayPaymentAdmin(admin.ModelAdmin):
    change_list_template = "razorpay_payments.html"  # Custom template

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.razorpay_payments_view), name="razorpay-payments")
        ]
        return custom_urls + urls

    def razorpay_payments_view(self, request):
        date_str = request.GET.get('date')
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            selected_date = timezone.now()

        start_time = int(selected_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        end_time = int(selected_date.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp())

        try:
            payments = razorpay_client.payment.all({
                'from': start_time,
                'to': end_time,
                'status': 'captured'
            })['items']
        except Exception as e:
            return HttpResponse(f"Error fetching payments: {e}")

        context = dict(
            self.admin_site.each_context(request),
            payments=payments,
            title="Successful Razorpay Payments",
            selected_date=selected_date.strftime('%Y-%m-%d')
        )
        return TemplateResponse(request, "razorpay_payments.html", context)






admin.site.register(Participant, ParticipantAdmin)
admin.site.register(RegistrationType)
#admin.site.register(Participant)
#admin.site.register(WorkshopPricing, WorkshopPricingAdmin)
admin.site.register(WorkshopPricing)
admin.site.register(ParticipantRegistration, ParticipantRegistrationAdmin)
admin.site.register(AimerMember, AimerMemberAdmin)

admin.site.register(District)
admin.site.register(State)

admin.site.register(RazorpayPayment, RazorpayPaymentAdmin)










