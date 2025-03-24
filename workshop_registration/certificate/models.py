from django.db import models
from registration.models import RegistrationType, Participant
from colorfield.fields import ColorField

class CertificateTemplate(models.Model):
    """
    Stores certificate templates for different workshops.
    Each workshop can have its unique template, fetched from a URL.
    """
    workshop = models.OneToOneField(
        RegistrationType,  # Links to the workshop type in the registration app
        on_delete=models.CASCADE,
        related_name='certificate_template',
        help_text="Workshop this template belongs to"
    )
    template_url = models.URLField(
        max_length=500,
        help_text="URL to fetch the certificate template (PNG, JPEG, or PDF)"
    )
    name_position_x = models.PositiveIntegerField(
        help_text="X-coordinate for placing participant's name on the template"
    )
    name_position_y = models.PositiveIntegerField(
        help_text="Y-coordinate for placing participant's name on the template"
    )
    font_size = models.PositiveIntegerField(
        default=40,
        help_text="Font size for the participant's name"
    )
    
    '''
    font_color = models.CharField(
        max_length=7,
        default="#000000",
        help_text="Font color for the participant's name in HEX (e.g., #000000)"
    )

    '''
    font_color = ColorField(
        default="#000000",
        help_text="Font color for the participant's name"
    )
    

    def __str__(self):
        return f"Template for {self.workshop.name}"


class CertificateStatus(models.Model):
    """
    Tracks if a certificate has been generated and sent to a participant.
    Handles participants who attend multiple workshops.
    """
    workshop = models.ForeignKey(
        RegistrationType,
        on_delete=models.CASCADE,
        related_name='certificate_status',
        help_text="Workshop attended"
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='certificate_status',
        help_text="Participant who attended the workshop"
    )
    certificate_sent = models.BooleanField(
        default=False,
        help_text="Has the certificate email been sent?"
    )
    sent_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of when the certificate was sent"
    )

    class Meta:
        unique_together = ('workshop', 'participant')

    def __str__(self):
        return f"{self.participant.name} - {self.workshop.name} - Sent: {self.certificate_sent}"

