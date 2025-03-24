import os
from pathlib import Path
from dotenv import load_dotenv

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
print("Inside settings/base")
print(BASE_DIR)

DJANGO_ENV = os.getenv("DJANGO_ENV", "local")

print(DJANGO_ENV)
# Load environment variables

if DJANGO_ENV == "docker":
    print("inside /base.py/DJANGO_ENV==docker")
    load_dotenv(BASE_DIR / ".env", override=True)
else:
    print("inside /base.py/else")
    load_dotenv(BASE_DIR / ".env_local", override=True)

#preliminary check
print(os.environ.get("key_id"))
print(os.environ.get("key_secret"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "your-default-secret-key")
print("Inside setting/base")
print("SECERET_KEY")
print(SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
print("Inside base settings")
print(os.environ.get("ALLOWED_HOSTS"))
print(ALLOWED_HOSTS)
print(ALLOWED_HOSTS)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "dashboard",
    "registration",
    "certificate",
    "colorfield"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "workshop_registration.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "workshop_registration.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = '/admin/login/'  # Redirects unauthenticated users to Django admin login


LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")

# Razorpay Credentials
RAZORPAY_KEY_ID = os.environ.get("key_id", "")
RAZORPAY_KEY_SECRET = os.environ.get("key_secret", "")




# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.hostinger.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

#default - email address
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")


# Separate accounts for receipts and certificates
EMAIL_ACCOUNTS = {
    'receipts': {
        'USER': os.environ.get('EMAIL_HOST_USER_RECEIPTS', ''),
        'PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD_RECEIPTS', '')
    },
    'certificates': {
        'USER': os.environ.get('EMAIL_HOST_USER_CERTIFICATES', ''),
        'PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD_CERTIFICATES', '')
    }
}




EMAIL_IMAP_HOST = "imap.hostinger.com"
EMAIL_IMAP_PORT = 993


# for certificate signing

# Add this line to specify the path to the keys folder
KEYS_DIR = os.path.join(BASE_DIR, 'workshop_registration/certificate', 'keys')

# Private Key Path
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, 'private_key.pem')

# Public Key Path (Optional, in case you need to verify the signature later)
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, 'public_key.pem')

print("Inside base settings, Private_key_path",PRIVATE_KEY_PATH)
print("Inside base settings, public_key_path", PUBLIC_KEY_PATH)