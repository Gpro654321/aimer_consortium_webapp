import json
import os
from django.core.management.base import BaseCommand
from registration.location_models import State, District  # Import your models

class Command(BaseCommand):
    help = "Load states and districts from a JSON file into the database"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), "../../../states_districts.json")

        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)

            for state_data in data['states']:
                state_name = state_data['state']
                districts = state_data['districts']

                state, created = State.objects.get_or_create(name=state_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added State: {state_name}"))

                for district_name in districts:
                    district, district_created = District.objects.get_or_create(name=district_name, state=state)
                    if district_created:
                        self.stdout.write(self.style.SUCCESS(f"  Added District: {district_name} under {state_name}"))

            self.stdout.write(self.style.SUCCESS("✅ Data successfully loaded into the database."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error loading data: {e}"))
