from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Participant, RegistrationType
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import WorkshopPricing
from datetime import date

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

"""
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration_type = form.cleaned_data['registration_type']
            participant_email = form.cleaned_data['email']

            # Check for existing AIMER registrations (for discount)
            existing_aimer_registration = Participant.objects.filter(
                email=participant_email,
                registration_type__name='AIMER',
                razorpay_payment_id__isnull=False  # Ensure successful payment
            ).exists()

            # Check for existing registrations (improved error handling)
            existing_registrations = Participant.objects.filter(
                email=participant_email,
                registration_type=registration_type,
                razorpay_payment_id__isnull=False  # Ensure successful payment
            )
            if existing_registrations.exists():
                return render(request, './already_registered.html', {'form': form})

            participant = form.save()  # Save participant data first
            amount = calculate_amount(registration_type, existing_aimer_registration)

            # Razorpay order creation
            order_data = {
                "amount": amount * 100,  # Convert to paise
                "currency": "INR",
                "receipt": f"order_rcptid_{participant.id}",
                "payment_capture": 1  # Auto capture payment
            }
            order = client.order.create(data=order_data)
            participant.razorpay_order_id = order['id']
            participant.save()  # Save order ID with participant

            context = {
                'order': order,
                'participant': participant,
                'key_id': settings.RAZORPAY_KEY_ID
            }
            return render(request, './payment.html', context)
        else:
            return render(request, './registration.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, './registration.html', {'form': form})

def calculate_amount(registration_type, existing_aimer_registration):
    amount = 0.00  # Default amount

    if registration_type.name == 'AIMER':
        amount = 2000.00
    elif registration_type.name == 'Workshop 1':
        if existing_aimer_registration:
            # Apply discount for Workshop 1 if already registered for AIMER
            amount = 1000.00 * 0.8  # Adjust discount percentage as needed
        else:
            amount = 1000.00
    # ... (add more conditions for other workshops)

    return amount


"""

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration_type = form.cleaned_data['registration_type']
            participant_email = form.cleaned_data['email']
            is_aimer_member = form.cleaned_data['is_aimer_member']

            # Check for existing registrations (improved error handling)
            existing_registrations = Participant.objects.filter(
                email=participant_email,
                registration_type=registration_type,
                razorpay_payment_id__isnull=False  # Ensure successful payment
            )
            if existing_registrations.exists():
                return render(request, './already_registered.html', {'form': form})

            participant = form.save()  # Save participant data first
            amount = calculate_amount(registration_type, is_aimer_member)

            # Razorpay order creation
            order_data = {
                "amount": amount * 100,  # Convert to paise
                "currency": "INR",
                "receipt": f"order_rcptid_{participant.id}",
                "payment_capture": 1  # Auto capture payment
            }
            order = client.order.create(data=order_data)
            participant.razorpay_order_id = order['id']
            participant.save()  # Save order ID with participant

            context = {
                'order': order,
                'participant': participant,
                'key_id': settings.RAZORPAY_KEY_ID
            }
            return render(request, './payment.html', context)
        else:
            return render(request, './registration.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, './registration.html', {'form': form})





def calculate_amount(registration_type, existing_aimer_registration):
    try:
        workshop_pricing = WorkshopPricing.objects.get(workshop_name=registration_type)
    except WorkshopPricing.DoesNotExist:
        # Handle the case where pricing is not configured for this workshop
        return 0.00  # Or raise an exception, or use a default price

    today = date.today()

    if workshop_pricing.cut_off_date and today > workshop_pricing.cut_off_date:
        amount = workshop_pricing.regular_price
    else:
        amount = workshop_pricing.early_bird_price

    if registration_type.name != 'AIMER' and existing_aimer_registration:
        amount = amount * 0.8  # Apply discount after cut off logic

    return amount

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', None)
        order_id = request.POST.get('razorpay_order_id', None)
        signature = request.POST.get('razorpay_signature', None)
        
        print(request.POST)
        
        razorpay_order = client.order.fetch(order_id)
        
        
        participant_id = int(razorpay_order['receipt'].split("_")[-1])
        print("razorpay_order")
        print(razorpay_order)
        print(participant_id)


        try:
            participant = Participant.objects.get(id=participant_id)
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)
            participant.razorpay_payment_id = payment_id
            participant.payment_status = True
            participant.save()

            return render(request, './payment_success.html')
        except Participant.DoesNotExist:
            print("Participant does not exist")
            return render(request, './payment_failed.html', {'error_message': "Participant does not exist"})
        except Exception as e:
            print(f"Payment verification error: {e}")
            return render(request, './payment_failed.html', {'error_message': str(e)})
    return redirect('registration')