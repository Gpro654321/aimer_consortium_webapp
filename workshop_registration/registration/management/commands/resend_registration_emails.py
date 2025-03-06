import logging
from django.core.management.base import BaseCommand
from registration.models import ParticipantRegistration
from registration.tasks import send_registration_email

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Resend registration emails to participants of a given workshop"

    def add_arguments(self, parser):
        parser.add_argument('workshop_name', type=str, help="Name of the workshop to resend emails for")

    def handle(self, *args, **options):
        workshop_name = options['workshop_name']

        # Fetch all participants who registered for the specified workshop
        registrations = ParticipantRegistration.objects.filter(registration_type__name=workshop_name)

        if not registrations.exists():
            self.stdout.write(self.style.WARNING(f"No participants found for workshop: {workshop_name}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {registrations.count()} participants. Sending emails..."))

        for registration in registrations:
            try:
                send_registration_email.delay(registration.id)  # Use Celery task to send email
                logger.info(f"Queued email for {registration.participant.email}")
                self.stdout.write(self.style.SUCCESS(f"Queued email for {registration.participant.email}"))
            except Exception as e:
                logger.error(f"Failed to queue email for {registration.participant.email}: {e}")
                self.stdout.write(self.style.ERROR(f"Failed for {registration.participant.email}: {e}"))

        self.stdout.write(self.style.SUCCESS("All emails have been queued for sending."))
