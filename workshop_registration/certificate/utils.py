import os
from django.conf import settings
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode
import hashlib
import base64
import fitz  # PyMuPDF
import logging

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import base64

# for dynamically switching between emails for different services
from django.core.mail import EmailMessage, get_connection
from django.conf import settings

logger = logging.getLogger(__name__)

TEMP_DIR = tempfile.gettempdir()

def convert_drive_link_to_direct(url):
    """
    Converts a Google Drive shareable link to a direct download link.
    Supports both 'file/d/FILE_ID/view' and 'open?id=FILE_ID' formats.
    """
    import re
    
    # Extract the file ID from different URL formats
    file_id_match = re.search(r'(?:file/d/|open\?id=)([a-zA-Z0-9_-]+)', url)
    
    if file_id_match:
        file_id = file_id_match.group(1)
        direct_link = f"https://drive.google.com/uc?id={file_id}&export=download"
        print(f"Direct Download Link: {direct_link}")
        return direct_link
    else:
        raise ValueError("Invalid Google Drive link format.")




def download_template(template_url):
    """
    Download the certificate template if not already present in TEMP_DIR.
    Returns the path to the downloaded template.
    
    """


    direct_url = convert_drive_link_to_direct(template_url)

    logger.info(direct_url)
    print(direct_url)

    filename = os.path.basename(direct_url)
    template_path = os.path.join(TEMP_DIR, filename)
    logger.info("Inside certificate/utils download_template")
    logger.info(template_path)

    if not os.path.exists(template_path):
        print(f"Downloading template from {direct_url}...")
        response = requests.get(direct_url)
        if response.status_code == 200:
            with open(template_path, 'wb') as f:
                f.write(response.content)
            print(f"Template saved at {template_path}")
        else:
            raise Exception(f"Failed to download template: {response.status_code}")
    else:
        print(f"Using cached template from {template_path}")

    return template_path






def load_private_key():
    """Load the private key from file."""
    private_key_path = os.path.join(settings.BASE_DIR,
                                     'workshop_registration/certificate/keys', 
                                     'private_key.pem')
    with open(private_key_path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

def generate_qr_code(participant):
    """Generate QR code with signed participant details."""
    private_key = load_private_key()

    # Data to be signed
    data = f"{participant.name}|{participant.email}".encode()

    # Sign the data with the private key
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Encode data and signature to Base64 for URL-friendly format
    encoded_message = base64.urlsafe_b64encode(data).decode()
    encoded_signature = base64.urlsafe_b64encode(signature).decode()

    # Generate QR code URL with your new endpoint
    qr_url = (
        f"https://aimerconsortium.labmasters.in/certificate/verify/"
        f"?message={encoded_message}&signature={encoded_signature}"
    )

    # Generate the QR code
    qr = qrcode.make(qr_url)
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)

    return qr_io




def generate_certificate(participant, certificate_template, private_key, output_format='pdf'):
    """
    Generate a certificate for a given participant with QR code in a white space below the certificate.
    1. Download the template once (if not cached).
    2. Create a larger canvas with white space below.
    3. Overlay the participant name.
    4. Add QR code to the white space.
    5. Return the final certificate as bytes or path.
    """
    # Step 1: Fetch Template
    template_path = download_template(certificate_template.template_url)

    # Step 2: Load the template (force JPEG handling)
    with open(template_path, 'rb') as f:
        template_bytes = io.BytesIO(f.read())
    
    template_image = Image.open(template_bytes)
    width, height = template_image.size

    # Step 3: Create Larger Canvas with White Space
    white_space_height = height  # White space height: 1/3 of the certificate height
    new_height = height + white_space_height

    # Create a new white canvas
    new_canvas = Image.new('RGB', (width, new_height), (255, 255, 255))
    
    # Paste the original certificate at the top
    new_canvas.paste(template_image, (0, 0))

    # Step 4: Overlay Participant Name
    draw = ImageDraw.Draw(new_canvas)

    # Construct the path to arial.ttf in the fonts folder
    font_path = os.path.join(settings.BASE_DIR, 
                             'workshop_registration/certificate', 
                             'fonts', 'arial.ttf')

    # Load the font with the correct path
    font = ImageFont.truetype(font_path, certificate_template.font_size)

    draw.text(
        (certificate_template.name_position_x, certificate_template.name_position_y),
        participant.name.title(),
        fill=certificate_template.font_color,
        font=font
    )

    # Step 5: Generate QR Code and Paste in White Space
    qr_code = generate_qr_code(participant)
    qr_image = Image.open(qr_code)

    # Resize QR Code if needed
    qr_size =  white_space_height // 2
    qr_image = qr_image.resize((qr_size, qr_size))

    # Calculate QR code position to center it in the white space
    qr_x = (width - qr_size) // 2
    qr_y = height + (white_space_height - qr_size) // 2

    new_canvas.paste(qr_image, (qr_x, qr_y))

    # Step 6: Convert the merged image to PDF with PyMuPDF
    certificate_pdf_path = os.path.join(TEMP_DIR, f"{participant.name.replace(' ', '_')}_certificate.pdf")

    # Save the final certificate with QR code as bytes
    merged_image_bytes = io.BytesIO()
    new_canvas.save(merged_image_bytes, format="PNG")
    merged_image_bytes.seek(0)

    # Create a new PDF with merged certificate + QR code as a single page
    doc = fitz.open()
    page = doc.new_page(width=new_canvas.width, height=new_canvas.height)
    page.insert_image(page.rect, stream=merged_image_bytes)

    # Save merged PDF
    doc.save(certificate_pdf_path)
    doc.close()

    # Step 7: Return Final PDF
    if output_format == 'bytes':
        with open(certificate_pdf_path, 'rb') as f:
            return f.read()
    else:
        return certificate_pdf_path




# Example Usage:
# Assuming `participant` and `certificate_template` are fetched from your Django models:
# participant = Participant.objects.get(email="example@example.com")
# certificate_template = CertificateTemplate.objects.get(workshop=workshop_instance)
# private_key = "your_private_key"
# pdf_path = generate_certificate(participant, certificate_template, private_key)
# print(f"Certificate generated at: {pdf_path}")




def send_email_with_service(service, subject, body, recipient_list, attachments=None, content_subtype="plain"):
    """
    Send email using a specific service ('receipts' or 'certificates').
    """
    # Get credentials for the selected service
    account = settings.EMAIL_ACCOUNTS.get(service, {})
    user = account.get("USER")
    password = account.get("PASSWORD")

    if not user or not password:
        raise ValueError(f"Email service '{service}' is not properly configured!")

    # Create custom connection
    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=user,
        password=password,
        use_tls=settings.EMAIL_USE_TLS,
    )

    # Create email
    email = EmailMessage(subject, body, user, recipient_list, connection=connection)

    # Attach files if any
    if attachments:
        for attachment in attachments:
            email.attach(*attachment)

    # Set content type if needed (e.g., 'html' for HTML emails)
    email.content_subtype = content_subtype

    # Send email
    email.send()
