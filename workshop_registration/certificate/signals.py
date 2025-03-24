from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from registration.models import ParticipantRegistration
from certificate.models import CertificateStatus


@receiver(pre_save, sender=ParticipantRegistration)
def handle_workshop_change(sender, instance, **kwargs):
    """
    Handles the scenario where a participant changes the workshop.
    If the workshop is updated, the old CertificateStatus entry is deleted.
    A new entry will be created in post_save.
    """
    # Check if the instance already exists in the database
    if instance.pk:
        old_instance = ParticipantRegistration.objects.get(pk=instance.pk)
        
        # Detect workshop change
        if old_instance.registration_type != instance.registration_type:
            # Delete the old certificate status
            CertificateStatus.objects.filter(
                participant=instance.participant,
                workshop=old_instance.registration_type
            ).delete()


@receiver(post_save, sender=ParticipantRegistration)
def create_certificate_status(sender, instance, created, **kwargs):
    """
    Automatically create CertificateStatus when a participant registers successfully for a workshop.
    """
    if instance.payment_status:
        CertificateStatus.objects.get_or_create(
            participant=instance.participant,
            workshop=instance.registration_type,
            defaults={'certificate_sent': False}
        )

@receiver(post_delete, sender=ParticipantRegistration)
def delete_certificate_status(sender, instance, **kwargs):
    """
    Automatically delete CertificateStatus when a participant registration is deleted.
    """
    CertificateStatus.objects.filter(
        participant=instance.participant,
        workshop=instance.registration_type
    ).delete()
