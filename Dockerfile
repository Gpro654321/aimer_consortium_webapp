FROM python:3.10-slim-buster

WORKDIR /code

# Install system dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

# Collect static files (important for production)
RUN python ./workshop_registration/manage.py collectstatic --noinput


WORKDIR /code/workshop_registration/

# Set the entrypoint to Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "workshop_registration.wsgi:application"]