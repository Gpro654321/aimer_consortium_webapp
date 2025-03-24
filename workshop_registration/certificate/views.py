from django.shortcuts import render

# Create your views here.
import os
from django.conf import settings
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

def load_public_key():
    """Load the public key from file."""
    public_key_path = os.path.join(settings.BASE_DIR, 
                                   'workshop_registration/certificate/keys', 
                                   'public_key.pem')
    with open(public_key_path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())

def verify_certificate(request):
    """Verify the certificate."""
    public_key = load_public_key()
    
    # Extract message and signature from URL
    encoded_message = request.GET.get("message", "")
    encoded_signature = request.GET.get("signature", "")

    try:
        # Decode message and signature
        message = base64.urlsafe_b64decode(encoded_message)
        signature = base64.urlsafe_b64decode(encoded_signature)

        # Verify the signature
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # If verification is successful
        name, email = message.decode().split("|")
        return render(request, './verification_success.html', 
                      {'name': name, 'email': email})

    except Exception as e:
        # If verification fails
        return render(request, './verification_failure.html')
