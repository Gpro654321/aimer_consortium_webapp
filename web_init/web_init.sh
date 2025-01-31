#!/bin/bash
set -e

touch ./testfile123
python manage.py makemigrations registration
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput
gunicorn --bind 0.0.0.0:8000 --workers 3 --threads 2 workshop_registration.wsgi:application

