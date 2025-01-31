from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Participant, RegistrationType, WorkshopPricing, ParticipantRegistration, AimerMember
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import WorkshopPricing
from datetime import date
import datetime
from django.utils import timezone

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

"""

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration_type = form.cleaned_data['registration_type']
            participant_email = form.cleaned_data['email']
            
            # Check for existing AIMER registrations (for discount)
            is_aimer_member = Participant.objects.filter(
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
            amount = calculate_amount(registration_type, is_aimer_member)
            print("amount",amount)

            # Razorpay order creation
            order_data = {
                "amount": (amount * 100),  # Convert to paise
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

"""

"""
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration_type = form.cleaned_data['registration_type']
            participant_email = form.cleaned_data['email']

            # Check for existing AIMER registrations (for discount and pre-selecting checkbox)
            is_aimer_member = Participant.objects.filter(
                email=participant_email,
                registration_type__name='AIMER',
                razorpay_payment_id__isnull=False  # Ensure successful payment
            ).exists()

            # Pre-select "is_aimer_member" field based on registration type or existing AIMER registration
            if registration_type.name == 'AIMER' or is_aimer_member:
                form.instance.is_aimer_member = True

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
            print("amount", amount)

            # Razorpay order creation
            order_data = {
                "amount": (amount * 100),  # Convert to paise
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
"""

"""
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
            participant.amount_paid = float(razorpay_order['amount_paid'])/100
            participant.save()

            return render(request, './payment_success.html')
        except Participant.DoesNotExist:
            print("Participant does not exist")
            return render(request, './payment_failed.html', {'error_message': "Participant does not exist"})
        except Exception as e:
            print(f"Payment verification error: {e}")
            return render(request, './payment_failed.html', {'error_message': str(e)})
    return redirect('registration')
"""

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration_type = form.cleaned_data['registration_type']
            participant_email = form.cleaned_data['email']
            participant_name = form.cleaned_data['name']
            participant_mobile_number = form.cleaned_data['mobile_number']


            # Get or create participant
            participant, created = Participant.objects.get_or_create(
                email=participant_email,
                defaults={
                    'name': participant_name, 
                    'mobile_number': participant_mobile_number
                    }
            )

            is_aimer_registration = registration_type.name == 'AIMER'

            print("is_aimer_registration",is_aimer_registration)

            # Check if existing Aimer member (for discount)
            existing_aimer_member = None
            if not is_aimer_registration:
                try:
                    existing_aimer_member = AimerMember.objects.get(participant=participant, is_active_member=True)
                except AimerMember.DoesNotExist:
                    pass

            amount = calculate_amount(registration_type, bool(existing_aimer_member))

            order = create_razorpay_order(participant, amount)

            # Create ParticipantRegistration without the payment
            participant_registration = ParticipantRegistration.objects.create(
                participant=participant,
                registration_type=registration_type,
                razorpay_order_id=order['id'],
                #amount_paid=amount
            )

            # Create AimerMember if registering for AIMER

            #if is_aimer_registration:
            #   AimerMember.objects.get_or_create(participant=participant)

            context = {
                'order': order,
                'participant': participant,
                'key_id': settings.RAZORPAY_KEY_ID
            }
            return render(request, './payment_automatic_redirect2.html', context)
        else:
            return render(request, './registration.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, './registration.html', {'form': form})


def create_razorpay_order(participant, amount):
    order_data = {
        "amount": int(amount * 100),  # Convert to paise (important to convert to int)
        "currency": "INR",
        "receipt": f"order_rcptid_{participant.id}",
        "payment_capture": 1
    }
    return client.order.create(data=order_data)


def calculate_amount(registration_type, existing_aimer_registration):
    try:
        workshop_pricing = WorkshopPricing.objects.get(workshop_name=registration_type)
    except WorkshopPricing.DoesNotExist:
        # Handle the case where pricing is not configured for this workshop
        return 0.00  # Or raise an exception, or use a default price

    today = date.today()

    if workshop_pricing.cut_off_date and today > workshop_pricing.cut_off_date:
        amount = float(workshop_pricing.regular_price)
    else:
        amount = float(workshop_pricing.early_bird_price)

    if registration_type.name != 'AIMER' and existing_aimer_registration:
        #amount = amount * 0.8  # Apply discount after cut off logic
        amount = float(workshop_pricing.aimer_member_price)

    return amount


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', None)
        order_id = request.POST.get('razorpay_order_id', None)
        signature = request.POST.get('razorpay_signature', None)

        print("Inside registration app, payment_success view fun - request.POST\n",request.POST)
        print("Inside registration app, payment_success view fun - order_id\n", order_id)

        razorpay_order = client.order.fetch(order_id)

        participant_id = int(razorpay_order['receipt'].split("_")[-1])
        print("Inside registration app - views - payment_success -razorpay_order\n",razorpay_order)
        
        print(participant_id)

        try:
            participant = Participant.objects.get(id=participant_id)
            
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)

            
            
            #participant.razorpay_payment_id = payment_id
            #participant.payment_status = True
            #participant.amount_paid = float(razorpay_order['amount_paid']) / 100
            participant.save()
            
            # update the payment id
            # update the registration time and date
            participant_registration = ParticipantRegistration.objects.filter(participant=participant).last()
            if participant_registration:
                participant_registration.amount_paid = float(razorpay_order['amount_paid']) / 100
                participant_registration.razorpay_payment_id = payment_id
                participant_registration.payment_status = True
                participant_registration.registered_at = timezone.now()  # Update to current time
                print("Inside registration app-payment success fn-register at\n",timezone.now())
                participant_registration.save()

            # Create AimerMember only if registering for AIMER and payment successful
            registration_type = ParticipantRegistration.objects.filter(participant=participant).last().registration_type
            if registration_type.name == 'AIMER':
                AimerMember.objects.get_or_create(participant=participant)

            return render(request, './payment_success.html')
        except Participant.DoesNotExist:
            print("Participant does not exist")
            return render(request, './payment_failed.html', {'error_message': "Participant does not exist"})
        except Exception as e:
            print(f"Payment verification error: {e}")
            return render(request, './payment_failed.html', {'error_message': str(e)})
    return redirect('registration')


