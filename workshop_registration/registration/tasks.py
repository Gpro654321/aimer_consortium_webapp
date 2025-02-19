import os
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from .models import ParticipantRegistration

@shared_task
def send_registration_email(participant_registration_id):
    """Send confirmation email asynchronously using Celery."""

    try:
        # Fetch participant registration instance
        participant_registration = ParticipantRegistration.objects.get(id=participant_registration_id)
        participant = participant_registration.participant
        workshop_name = participant_registration.registration_type.name

        # Fetch WhatsApp group link
        whatsapp_link = participant_registration.registration_type.workshop_pricings.first().whatsapp_group_link

        # Generate PDF Receipt
        pdf_buffer = generate_receipt(participant_registration)

        # Prepare email message
        subject = f"Workshop Registration Confirmation - {workshop_name}"
        message = render_to_string('confirmation_email.html', {
            'name': participant.name,
            'workshop': workshop_name,
            'whatsapp_link': whatsapp_link
        })

        # Create email with PDF attachment
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [participant.email]
        )
        email.attach(
            f"Receipt_{participant.name}_{workshop_name}.pdf",
            pdf_buffer.getvalue(),
            "application/pdf"
        )
        email.content_subtype = "html"  # Ensure HTML format
        email.send()

    except Exception as e:
        print(f"Email sending failed: {e}")


def generate_receipt(participant_registration):
    """Generate a professionally styled PDF receipt with structured formatting."""

    buffer = BytesIO()
    width, height = A4  # Standard A4 page size

    # Create canvas
    p = canvas.Canvas(buffer, pagesize=A4)

    # Load and register a font with Unicode support
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    p.setFont("DejaVuSans", 12)

    # ✅ Add AIMER Consortium logo at the top left
    logo_path = os.path.join(settings.BASE_DIR, "workshop_registration/registration/static/registration", "images", "AIMER_logo.jpeg")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        p.drawImage(logo, 50, height - 90, width=120, height=60, preserveAspectRatio=True, mask='auto')

    # ✅ Add "AIMER CONSORTIUM" Title (Centered)
    p.setFillColor(colors.darkblue)
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(width / 2, height - 60, "AIMER CONSORTIUM")

    # ✅ Add Website Below Title
    p.setFont("Helvetica-Oblique", 12)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, height - 80, "https://register.aimerconsortium.in")

    # ✅ Draw horizontal separator line (after some spacing)
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(40, height - 110, width - 40, height - 110)

    # ✅ Background shading for "PAYMENT RECEIPT"
    p.setFillColor(colors.lightgrey)
    p.rect(40, height - 145, width - 80, 30, fill=True, stroke=False)

    # ✅ Add "PAYMENT RECEIPT" Title (Centered)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 130, "PAYMENT RECEIPT")

    # ✅ Reset font and text color for details
    p.setFillColor(colors.black)
    p.setFont("DejaVuSans", 12)

    # ✅ Align ":" in the same column
    details = {
        "Participant Name": participant_registration.participant.name,
        "Email": participant_registration.participant.email,
        "Phone": participant_registration.participant.mobile_number,
        "Workshop": participant_registration.registration_type.name,
        "Amount Paid": f"Rs {participant_registration.amount_paid}",
        "Payment ID": participant_registration.razorpay_payment_id,
        "Registration Date": participant_registration.registered_at.strftime('%d-%m-%Y'),
    }

    x_label = 100  # Left-aligned labels
    x_value = 280  # Right-aligned values
    y_position = height - 200  # Adjust vertical spacing

    for label, value in details.items():
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_label, y_position, f"{label}")  # Consistent label width
        p.setFont("Helvetica", 12)
        p.drawString(x_value, y_position, value)
        y_position -= 30  # More spacing for clarity

    # ✅ Add footer
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.grey)
    p.drawString(100, 50, "Thank you for registering! For queries, contact support@aimerconsortium.in")

    # ✅ Save and return PDF
    p.showPage()
    p.save()
    buffer.seek(0)

    return buffer

