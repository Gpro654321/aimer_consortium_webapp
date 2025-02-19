from .base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_NAME", "your_local_db_name"),
        "USER": os.environ.get("POSTGRES_USER", "your_local_db_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "your_local_db_password"),
        "HOST": "localhost",  # Running locally
        "PORT": "5432",
    }
}

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1"]

# Celery Configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"  # Redis as the broker
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"