#!/bin/bash
set -e


touch ./testfile123

python manage.py makemigrations registration
python manage.py makemigrations certificate
python manage.py migrate
python manage.py migrate django_celery_beat
python manage.py collectstatic --noinput
#python manage.py createsuperuser --noinput
#gunicorn --bind 0.0.0.0:8000 --workers 3 --threads 2 workshop_registration.wsgi:application
#gunicorn --bind 0.0.0.0:8000 --workers 3 --threads 2 --log-level debug --access-logfile - --error-logfile - workshop_registration.wsgi:application

# Start supervisord to manage Gunicorn and Celery
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
