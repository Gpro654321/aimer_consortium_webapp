from django.core.management.base import BaseCommand
from registration.models import ParticipantRegistration
from certificate.models import CertificateStatus
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Creates CertificateStatus entries for all paid participants in a given workshop'

    def add_arguments(self, parser):
        parser.add_argument('workshop_id', type=int, help='ID of the workshop')

    def handle(self, *args, **kwargs):
        workshop_id = kwargs['workshop_id']

        # Fetch all participants with successful payments for the given workshop
        registrations = ParticipantRegistration.objects.filter(
            registration_type_id=workshop_id,
            payment_status=True
        ).select_related('participant')

        if not registrations.exists():
            self.stdout.write(self.style.WARNING(f"No paid participants found for workshop ID {workshop_id}."))
            return

        created_count = 0
        skipped_count = 0

        # Create CertificateStatus entries only if they don't exist
        for registration in registrations:
            cert_status, created = CertificateStatus.objects.get_or_create(
                participant=registration.participant,
                workshop=registration.registration_type,
                defaults={'certificate_sent': False}
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"CertificateStatus created: {created_count}, Skipped: {skipped_count}"))

# example usage python manage.py create_certificate_status <workshop_id>
# LOOK AT REGISTRATION TYPES FOR THE <workshop_id>