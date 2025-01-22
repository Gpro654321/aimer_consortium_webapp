from django.contrib import admin

# Register your models here.

from .models import RegistrationType, WorkshopPricing, \
                    Participant, ParticipantRegistration, \
                    AimerMember


admin.site.register(RegistrationType)
admin.site.register(Participant)
admin.site.register(WorkshopPricing)
admin.site.register(ParticipantRegistration)
admin.site.register(AimerMember)
