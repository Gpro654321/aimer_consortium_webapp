import os
import razorpay
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from registration.models import ParticipantRegistration, AimerMember
from registration.tasks import send_registration_email

# Initialize Razorpay client with your API credentials
RAZORPAY_API_KEY = os.environ.get("key_id")
RAZORPAY_API_SECRET = os.environ.get("key_secret")
print(RAZORPAY_API_KEY, RAZORPAY_API_SECRET)

razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))


class Command(BaseCommand):
    help = "Reconcile payments for a specific date or the past 5 hours by default."

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Reconcile payments for a specific date (format: YYYY-MM-DD).'
        )

    def handle(self, *args, **options):
        # Determine date range for reconciliation
        if options['date']:
            try:
                reconciliation_date = datetime.datetime.strptime(options['date'], '%Y-%m-%d').date()
                start_time = datetime.datetime.combine(reconciliation_date,
                                                       datetime.time.min, tzinfo=datetime.timezone.utc)
                end_time = datetime.datetime.combine(reconciliation_date,
                                                     datetime.time.max, tzinfo=datetime.timezone.utc)
                self.stdout.write(f"Reconciling payments for {reconciliation_date}")
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))
                return
        else:
            end_time = timezone.now()
            start_time = end_time - datetime.timedelta(hours=5)
            self.stdout.write("Reconciling payments for the past 5 hours")

        print("start_time, ", start_time)
        print("end_time, ", end_time)

        # Fetch unpaid registrations in the time range
        pending_registrations = ParticipantRegistration.objects.filter(
            payment_status=False,
            registered_at__range=(start_time, end_time)
        )

        self.stdout.write(f"Found {pending_registrations.count()} unpaid registrations to reconcile.")

        for registration in pending_registrations:
            participant = registration.participant
            phone_number = participant.mobile_number[-10:]  # Last 10 digits of the phone number
            email = participant.email
            registration_type = registration.registration_type.name
            order_id = registration.razorpay_order_id

            self.stdout.write(
                f"\nChecking: {participant.name} | {phone_number} | {email} | {registration_type}"
            )

            # Query successful payments from Razorpay
            try:
                payments = razorpay_client.payment.all({
                    'from': int(start_time.timestamp()),
                    'to': int(end_time.timestamp()),
                    'contact': "+91" + phone_number
                })['items']

                for payment in payments:
                    if payment['status'] == 'captured' and \
                            registration_type in payment['description'] and \
                            order_id in payment['order_id']:

                        self.stdout.write(self.style.SUCCESS(
                            f"Match Found, Registration Type: {registration.registration_type.name}, "
                            f"Participant: {registration.participant.name}, Payment ID: {payment['id']}, "
                            f"Order ID: {payment['order_id']}"
                        ))
                        print(payment)
                        print("\n")

                        # Update ParticipantRegistration
                        registration.payment_status = True
                        registration.razorpay_payment_id = payment['id']
                        registration.registered_at = timezone.now()
                        registration.save()

                        # If the registration type is "AIMER", create an AimerMember entry
                        if registration_type == "AIMER":
                            aimer_member, created = AimerMember.objects.get_or_create(
                                participant=participant,
                                defaults={'is_active_member': True}
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(
                                    f"AIMER Membership created for {participant.name}."
                                ))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f"{participant.name} is already an AIMER Member."
                                ))

                        # ✅ Trigger email sending using Celery task
                        send_registration_email.delay(registration.id)
                        self.stdout.write(self.style.SUCCESS(
                            f"Email task triggered for {registration.participant.name} ({registration.participant.email})"
                        ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching payments: {e}"))
