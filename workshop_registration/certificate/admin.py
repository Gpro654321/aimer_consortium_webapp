from django.contrib import admin
from .models import CertificateTemplate, CertificateStatus


@admin.register(CertificateStatus)
class CertificateStatusAdmin(admin.ModelAdmin):
    list_display = (
        'participant_name',
        'participant_email',
        'participant_mobile',
        'workshop_name',
        'certificate_sent',
        'sent_on'
    )
    search_fields = (
        'participant__name',
        'participant__email',
        'participant__mobile_number',
        'workshop__name'
    )
    list_filter = ('certificate_sent', 'sent_on')

    def participant_name(self, obj):
        return obj.participant.name
    participant_name.short_description = 'Participant Name'

    def participant_email(self, obj):
        return obj.participant.email
    participant_email.short_description = 'Email'

    def participant_mobile(self, obj):
        return obj.participant.mobile_number
    participant_mobile.short_description = 'Mobile Number'

    def workshop_name(self, obj):
        return obj.workshop.name
    workshop_name.short_description = 'Workshop'


admin.site.register(CertificateTemplate)
