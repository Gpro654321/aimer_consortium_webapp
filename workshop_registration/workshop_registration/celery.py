import os
from celery import Celery

# Load DJANGO_ENV (default is "local")
DJANGO_ENV = os.getenv("DJANGO_ENV", "local")

# Dynamically set the settings module based on the environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"workshop_registration.settings.{DJANGO_ENV}")

app = Celery("workshop_registration")

# Load settings from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in installed Django apps
app.autodiscover_tasks()
