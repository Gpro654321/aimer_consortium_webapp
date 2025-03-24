from celery import shared_task
from django.utils.timezone import now, timedelta
from .utils import generate_certificate, download_template, load_private_key, send_email_with_service
from .models import CertificateStatus, CertificateTemplate
import time
import logging

logger = logging.getLogger(__name__)

EMAIL_LIMIT = 200
EMAIL_SUBJECT = "Your Workshop Participation Certificate"
EMAIL_BODY = """
Dear {name},

Thank you for participating in the workshop: {workshop_name}.
Please find your certificate attached.

Best regards,
AIMER Team
"""

@shared_task
def generate_and_send_certificates(workshop_id, offset=0):
    logger.info(f"Starting certificate generation for workshop_id: {workshop_id} | Offset: {offset}")

    # Fetch the template once
    try:
        template = CertificateTemplate.objects.get(workshop_id=workshop_id)
        template_path = download_template(template.template_url)
    except CertificateTemplate.DoesNotExist:
        logger.error(f"Certificate template not found for workshop ID {workshop_id}!")
        return

    # Load private key once (no need to pass it around)
    try:
        private_key = load_private_key()
        
    except FileNotFoundError:
        logger.error("Private key not found! Certificates cannot be generated.")
        return

    # Get unsent certificates and prefetch related participant data, limiting to EMAIL_LIMIT
    unsent_certificates = CertificateStatus.objects.filter(
        workshop_id=workshop_id, certificate_sent=False
    ).select_related('workshop', 'participant')[offset:offset + EMAIL_LIMIT]

    total_participants = unsent_certificates.count()
    logger.info(f"Processing {total_participants} participants (Offset: {offset})")

    emails_sent = 0

    # Process each participant
    for cert_status in unsent_certificates:
        participant = cert_status.participant

        # Generate certificate
        try:
            certificate_file = generate_certificate(
                participant, template, private_key, 'bytes'
            )
        except Exception as e:
            logger.error(f"Error generating certificate for {participant.name}: {e}")
            continue

        # Prepare email content
        email_subject = EMAIL_SUBJECT
        email_body = EMAIL_BODY.format(name=participant.name, workshop_name=cert_status.workshop.name)

        # Send email using send_email_with_service from utils.py
        try:
            send_email_with_service(
                    'certificates',  # Service name (choose as per your settings)
                    email_subject,
                    email_body,
                    [participant.email],  # Recipient list should be a list
                    [(f"{participant.name}_certificate.pdf", certificate_file, 'application/pdf')]
                )
            emails_sent += 1

            # Update CertificateStatus
            cert_status.certificate_sent = True
            cert_status.sent_on = now()
            cert_status.save()
            logger.info(f"Certificate sent to {participant.email} ({emails_sent}/{EMAIL_LIMIT})")

        except Exception as e:
            logger.error(f"Failed to send email to {participant.email}: {e}")
            continue

        # Small delay to avoid hitting the server too fast
        time.sleep(0.2)

    logger.info(f"Batch completed: {emails_sent} certificates sent.")

    # If there are more participants to process, queue the task again
    if total_participants == EMAIL_LIMIT:
        logger.info("Email limit reached. Queuing the next batch.")
        generate_and_send_certificates.apply_async(
            args=[workshop_id, offset + EMAIL_LIMIT],
            eta=now() + timedelta(days=1)  # Delay before the next batch
        )

    else:
        logger.info("All certificates processed.")
