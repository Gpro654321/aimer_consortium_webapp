import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from faker import Faker
from registration.models import Participant, State, District, RegistrationType, WorkshopPricing, ParticipantRegistration

fake = Faker()

class Command(BaseCommand):
    help = "Populate 100 random participants and assign them to workshops."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Generating dummy participants..."))

        # Get existing states and districts
        states = list(State.objects.all())
        districts = list(District.objects.all())

        # Ensure we have some registration types & workshops
        registration_types = list(RegistrationType.objects.all())
        workshops = list(WorkshopPricing.objects.all())

        if not states or not districts:
            self.stdout.write(self.style.ERROR("No states or districts found! Load them first."))
            return

        if not registration_types or not workshops:
            self.stdout.write(self.style.ERROR("No registration types or workshops found! Create them first."))
            return

        # Generate 100 random participants
        participants = []
        for _ in range(100):
            state = random.choice(states)
            district = random.choice(districts)

            participant = Participant(
                            name=fake.name(),
                            email=fake.unique.email(),
                            mobile_number=fake.phone_number()[:20],  # Trim phone number to 20 characters
                            designation=fake.job()[:255],  # Ensure designation fits in 255 chars
                            department=fake.word()[:255],  
                            institute=fake.company()[:255],  
                            gender=random.choice(["M", "F", "O"]),
                            state=state,
                            district=district
                        )
            participants.append(participant)

        # Bulk insert participants
        Participant.objects.bulk_create(participants)
        self.stdout.write(self.style.SUCCESS("✅ 100 Participants Created!"))

        # Fetch all newly created participants
        participants = list(Participant.objects.all())

        # Register each participant to a random workshop
        registrations = []
        for participant in participants:
            workshop = random.choice(workshops)
            registration_type = random.choice(registration_types)

            registration = ParticipantRegistration(
                participant=participant,
                registration_type=registration_type,
                razorpay_order_id="fake_order"+fake.word()[:10],
                razorpay_payment_id="fake_pay"+fake.word()[:10],
                payment_status=random.choice([True, False]),  # Simulate paid & unpaid registrations
                amount_paid=random.choice([0.00, workshop.early_bird_price, workshop.regular_price]),
            )
            registrations.append(registration)

        # Bulk insert registrations
        ParticipantRegistration.objects.bulk_create(registrations)
        self.stdout.write(self.style.SUCCESS("✅ Participants Registered to Workshops!"))

        self.stdout.write(self.style.SUCCESS("🎉 Dummy data generation complete. Check your dashboard!"))
