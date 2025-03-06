import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from registration.models import Participant, RegistrationType, ParticipantRegistration, AimerMember

class Command(BaseCommand):
    help = "Import participants from a CSV file and register them for a workshop"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument("workshop", type=str, help="Workshop name to register participants")

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file"]
        workshop_name = kwargs["workshop"].strip()

        try:
            # Get or create the workshop
            workshop, _ = RegistrationType.objects.get_or_create(name=workshop_name)
            print("workshop is ",workshop)

            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    email = row["Email Address"].strip().lower()
                    timestamp = row.get("Timestamp", "").strip()
                    payment_id = row.get("Razorpay transaction number", "").strip()
                    amount_paid = row.get("amount_paid").strip()

                    if not email:
                        self.stderr.write(self.style.ERROR("Skipping row: Missing email"))
                        continue

                    try:
                        # Convert Timestamp to Date
                        from datetime import datetime

                        formats = ["%Y/%m/%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"]

                        for fmt in formats:
                            try:
                                registered_at = datetime.strptime(timestamp, fmt)
                                break  # Exit the loop if parsing is successful
                            except ValueError:
                                continue  # Try the next format if this one fails
                        else:
                            # This runs only if all formats fail
                            self.stderr.write(self.style.ERROR(f"Skipping row: Invalid timestamp format '{timestamp}'"))
                            continue  # Skip to the next row


                        # Create or update participant
                        participant, created = Participant.objects.get_or_create(
                            email=email,
                            defaults={
                                "name": row["Name"].strip(),
                                "mobile_number": row.get("Mobile number (Preferably Whatsapp number)", "").strip(),
                                "designation": row.get("Designation", "").strip(),  # Fix spelling
                                "department": row.get("Department", "").strip(),
                                "institute": row.get("Institution", "").strip(),
                            }
                        )

                        if workshop.name == "AIMER":
                            # Create AIMER membership if it doesn't exist
                            aimer_member, created = AimerMember.objects.get_or_create(participant=participant)
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"Marked {participant.name} as an AIMER Member"))


                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Added: {participant.name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Skipped (Already exists): {participant.email}"))

                        # Register participant for the workshop
                        registration, created = ParticipantRegistration.objects.get_or_create(
                            participant=participant,
                            registration_type=workshop,
                            defaults={
                                "razorpay_order_id": "order_mancrete",
                                "razorpay_payment_id": payment_id if payment_id else None,
                                "payment_status": True,
                                "amount_paid": amount_paid,  # Decimal field
                                "registered_at": registered_at,
                            }
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(
                                f"Registered {participant.name} for {workshop_name} with payment ID {payment_id}"
                            ))
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"{participant.name} is already registered for {workshop_name}"
                            ))

                    except IntegrityError:
                        self.stderr.write(self.style.ERROR(f"Duplicate email found: {email}"))

            self.stdout.write(self.style.SUCCESS("CSV Import Completed!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
