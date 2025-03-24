from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .forms import RegistrationForm
from .models import Participant, RegistrationType, WorkshopPricing, ParticipantRegistration, AimerMember
from .location_models import State, District
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import WorkshopPricing
from datetime import date
import datetime
from django.utils import timezone

from .tasks import send_registration_email  # Import Celery task

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

"""
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                registration_type = form.cleaned_data['registration_type']
                participant_email = form.cleaned_data['email']
                participant_name = form.cleaned_data['name']
                participant_mobile_number = form.cleaned_data['mobile_number']
                participant_designation = form.cleaned_data['designation']
                participant_department = form.cleaned_data['department']
                participant_institute = form.cleaned_data['institute']


                # Get or create participant
                participant, created = Participant.objects.get_or_create(
                    email=participant_email,
                    defaults={
                        'name': participant_name, 
                        'mobile_number': participant_mobile_number,
                        'designation': participant_designation,
                        'department': participant_department,
                        'institute': participant_institute
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

                #amount = calculate_amount(registration_type, bool(existing_aimer_member))

                #order = create_razorpay_order(participant, amount)

                '''
                # Create ParticipantRegistration without the payment
                participant_registration = ParticipantRegistration.objects.create(
                    participant=participant,
                    registration_type=registration_type,
                    razorpay_order_id=order['id'],
                    #amount_paid=amount
                )
                '''
                
                
                # 🚀 **Step 1: Check if there's an existing paid registration**
                existing_paid_registration = ParticipantRegistration.objects.filter(
                    participant=participant,
                    registration_type=registration_type,
                    payment_status=True  # Only check fully paid registrations
                ).exists()

                if existing_paid_registration:
                    form.add_error(None, "You have already registered and paid for this workshop.")
                    return render(request, './registration.html', {'form': form})

                # 🚀 **Step 2: Try to find an unpaid registration**
                try:
                    participant_registration = ParticipantRegistration.objects.get(
                        participant=participant,
                        registration_type=registration_type,
                        payment_status=False  # Unpaid registrations only
                    )
                except ParticipantRegistration.DoesNotExist:
                    # No unpaid registration found, so create a new one
                    participant_registration = ParticipantRegistration(
                        participant=participant,
                        registration_type=registration_type
                    )

                # 🚀 **Step 3: Create new Razorpay order and update registration**
                #amount = calculate_amount(registration_type, False)
                amount = calculate_amount(registration_type, bool(existing_aimer_member))
                order = create_razorpay_order(participant, amount)

                participant_registration.razorpay_order_id = order['id']
                participant_registration.amount_paid = amount
                participant_registration.save()


                
                # Create AimerMember if registering for AIMER

                #if is_aimer_registration:
                #   AimerMember.objects.get_or_create(participant=participant)

                context = {
                    'order': order,
                    'participant': participant,
                    'key_id': settings.RAZORPAY_KEY_ID
                }
                return render(request, './payment_automatic_redirect2.html', context)
            except ValidationError as e:
                form.add_error(None, str(e))  # Add the error to the form's non-field errors
                return render(request, './registration.html', {'form': form})

        else:
            return render(request, './registration.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, './registration.html', {'form': form})
"""


def _get_or_create_participant(cleaned_data):
    """
    Retrieves an existing participant by email or creates a new one.
    """

    """
    Retrieves an existing participant by email or creates a new one.
    Converts state and district from ID to model instances.
    """
    #state_instance = State.objects.get(id=cleaned_data['state'])  # ✅ Convert ID to Model Instance
    #district_instance = District.objects.get(id=cleaned_data['district'])  # ✅ Convert ID to Model Instance

    participant, created = Participant.objects.get_or_create(
        email=cleaned_data['email'],
        defaults={
            'name': cleaned_data['name'],
            'mobile_number': cleaned_data['mobile_number'],
            'designation': cleaned_data['designation'],
            'department': cleaned_data['department'],
            'institute': cleaned_data['institute'],

            'gender': cleaned_data['gender'],
            'state': cleaned_data['state'],
            'district': cleaned_data['district'],
        }
    )
    return participant

def _get_existing_registration(participant, registration_type):
    """
    Checks for an existing paid or unpaid registration.
    Returns the unpaid registration if found; otherwise, None.
    """
    if ParticipantRegistration.objects.filter(participant=participant, registration_type=registration_type, payment_status=True).exists():
        return "PAID"

    try:
        return ParticipantRegistration.objects.get(participant=participant, registration_type=registration_type, payment_status=False)
    except ParticipantRegistration.DoesNotExist:
        return None

def _get_searchable_data():
    """
    Fetches states and districts from the database to populate searchable dropdowns.
    """
    states = State.objects.all().order_by("name")
    districts = District.objects.all().order_by("name")
    return {'states': states, 'districts': districts}

def _validate_aimer_registration(cleaned_data):
    """
    Checks if a participant is eligible to register for AIMER.
    Conditions:
    - If `WorkshopPricing.open_for_all` is False for AIMER:
      - Participant must have attended (paid for) at least one previous workshop.
      - Participant should not have already registered for AIMER.
    """
    try:
        registration_type = cleaned_data['registration_type']
        print("Inside validate_aimer_registration/views")
        print(registration_type)
        
        # Check if the selected registration type is AIMER
        if registration_type.name != 'AIMER':
            return None  # No restriction for other registration types

        # Fetch WorkshopPricing details for AIMER
        workshop_pricing = WorkshopPricing.objects.get(workshop_name=registration_type)
        print("Inside validate_aimer_registration/views")
        print(workshop_pricing)

        # If open_for_all is True, allow registration
        if workshop_pricing.is_open_for_all:
            return None  

        # Get the participant based on email
        participant = Participant.objects.filter(email=cleaned_data['email']).first()
        
        if not participant:
            return "You must have attended a workshop to register for AIMER."

        # Check if the participant has attended (paid) at least one workshop
        has_paid_workshop = ParticipantRegistration.objects.filter(
            participant=participant, payment_status=True
        ).exclude(registration_type=registration_type).exists()

        if not has_paid_workshop:
            return "Only participants who have attended a paid workshop can register for AIMER."
        

        '''
         # Ensure they haven't already registered for AIMER
        already_registered = ParticipantRegistration.objects.filter(
            participant=participant, registration_type=registration_type
        ).exists()
        '''
        already_registered=_get_existing_registration(participant, registration_type)

        if already_registered == "PAID":
            return "You have already registered for AIMER."

        return None  # No validation errors, registration is allowed.

    except WorkshopPricing.DoesNotExist:
        return "Workshop pricing information is missing for AIMER."


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if not form.is_valid():
            #return render(request, './registration.html', {'form': form})
            return render(request, './registration.html', {'form': form, **_get_searchable_data()})

        try:
            cleaned_data = form.cleaned_data
            registration_type = cleaned_data['registration_type']
            is_aimer_registration = registration_type.name == 'AIMER'

            # 🔹 Validate AIMER Registration (if applicable)
            error_message = _validate_aimer_registration(cleaned_data)
            if error_message:
                form.add_error(None, error_message)
                return render(request, './registration.html', {'form': form, **_get_searchable_data()})

            participant = _get_or_create_participant(cleaned_data)

            # Check if participant is already an active AIMER member
            existing_aimer_member = AimerMember.objects.filter(participant=participant, is_active_member=True).first()

            # Check for existing registrations
            existing_registration = _get_existing_registration(participant, registration_type)
            if existing_registration == "PAID":
                form.add_error(None, "You have already registered and paid for this workshop.")
                #return render(request, './registration.html', {'form': form})
                return render(request, './registration.html', {'form': form, **_get_searchable_data()})

            # Create or retrieve an unpaid registration
            if existing_registration is None:
                participant_registration = ParticipantRegistration(participant=participant, registration_type=registration_type)
            else:
                participant_registration = existing_registration

            # Create Razorpay order
            amount = calculate_amount(registration_type, bool(existing_aimer_member))

            
            if amount == 0:
                #execute this block if the amount is zero. Sometimes AIMER members have this priviledge
                form.add_error(None, "You can attend for FREE")
                #return render(request, './registration.html', {'form': form})
                return render(request, './registration.html', {'form': form, **_get_searchable_data()}) 

            order = create_razorpay_order(participant, amount)

            # Update and save registration details
            participant_registration.razorpay_order_id = order['id']
            participant_registration.amount_paid = amount
            participant_registration.save()

            # Prepare context for payment page
            context = {
                'order': order,
                'participant': participant,
                'key_id': settings.RAZORPAY_KEY_ID,
                'registration_type_name': registration_type.name
            }
            return render(request, './payment_automatic_redirect2.html', context)

        except ValidationError as e:
            form.add_error(None, str(e))
            #return render(request, './registration.html', {'form': form})
            return render(request, './registration.html', {'form': form, **_get_searchable_data()})
        
        

    else:
        form = RegistrationForm()
        #return render(request, './registration.html', {'form': form})
        return render(request, './registration.html', {'form': form, **_get_searchable_data()})



def create_razorpay_order(participant, amount):
    order_data = {
        "amount": int(amount * 100),  # Convert to paise (important to convert to int)
        "currency": "INR",
        "receipt": f"order_rcptid_{participant.id}",
        "payment_capture": 1
    }
    return client.order.create(data=order_data)


def calculate_amount(registration_type, existing_aimer_registration):
    print("/calculate amount/views")
    print("existing_aimer_registration")
    try:
        workshop_pricing = WorkshopPricing.objects.get(workshop_name=registration_type)
    except WorkshopPricing.DoesNotExist:
        # Handle the case where pricing is not configured for this workshop
        return 0.00  # Or raise an exception, or use a default price

    today = date.today()

    if workshop_pricing.cut_off_date and today > workshop_pricing.cut_off_date:
        amount = float(workshop_pricing.regular_price)
        print("/if/calculate_amount/")
        print(amount)
    else:
        amount = float(workshop_pricing.early_bird_price)
        print("/else/calculate_amount")
        print(amount)

    if registration_type.name != 'AIMER' and existing_aimer_registration:
        #amount = amount * 0.8  # Apply discount after cut off logic
        amount = float(workshop_pricing.aimer_member_price)
        print("/second if/registration_type !=AIMER")
        print(amount)

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

            # **Trigger Celery Task for sending email**
            send_registration_email.delay(participant_registration.id)

            return render(request, './payment_success.html')
        except Participant.DoesNotExist:
            print("Participant does not exist")
            return render(request, './payment_failed.html', {'error_message': "Participant does not exist"})
        except Exception as e:
            print(f"Payment verification error: {e}")
            return render(request, './payment_failed.html', {'error_message': str(e)})
    return redirect('registration')


