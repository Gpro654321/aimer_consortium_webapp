from django.test import TestCase, Client
from .models import Participant, RegistrationType, WorkshopPricing, ParticipantRegistration, AimerMember
from datetime import date, timedelta
from unittest.mock import patch
from django.urls import reverse
import datetime

class RegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.aimer_type = RegistrationType.objects.create(name="AIMER")
        self.workshop_type = RegistrationType.objects.create(name="Workshop 1")
        self.workshop_pricing = WorkshopPricing.objects.create(
            workshop_name=self.workshop_type, early_bird_price=1000, regular_price=1200,
            cut_off_date=date.today() + timedelta(days=7)
        )
        self.aimer_pricing = WorkshopPricing.objects.create(
            workshop_name=self.aimer_type, early_bird_price=2000, regular_price=2500
        )
        self.registration_url = reverse('registration')
        self.payment_success_url = reverse('payment_success')

    def test_register_for_aimer(self):
        participant_data = {
            "name": "Test User",
            "email": "test@example.com",
            "mobile_number": "1234567890",
            "registration_type": self.aimer_type.id
        }
        with patch('registration.views.client') as mock_client:
            mock_client.order.create.return_value = {
                'id': 'test_order_id',
                'receipt': f"order_rcptid_1",
                'amount': 200000
            }
            response = self.client.post(self.registration_url, participant_data)

            self.assertEqual(response.status_code, 200)  # Expecting a redirect

            participant = Participant.objects.get(email="test@example.com")
            self.assertEqual(ParticipantRegistration.objects.count(), 1)
            self.assertEqual(AimerMember.objects.count(), 0)

            registration = ParticipantRegistration.objects.last()
            self.assertEqual(registration.registration_type, self.aimer_type)
            self.assertNotEqual(registration.amount_paid, 2000)

            payment_data = {
                'razorpay_payment_id': "pay_test",
                'razorpay_order_id': 'test_order_id',
                'razorpay_signature': 'test_signature'
            }

            with patch('registration.views.client.utility.verify_payment_signature') as mock_verify_signature:
                with patch('registration.views.client.order.fetch') as mock_order_fetch:
                    mock_order_fetch.return_value = {
                            'id': 'test_order_id', 
                            'entity': 'order', 
                            'amount': 200000, 
                            'amount_paid': 200000, 
                            'amount_due': 0, 
                            'currency': 'INR', 
                            'receipt': 'order_rcptid_1', 
                            'offer_id': None, 
                            'status': 'paid', 
                            'attempts': 1, 
                            'notes': [], 
                            'created_at': 1737564274
                    }

                    mock_verify_signature.return_value = None

                    response = self.client.post(self.payment_success_url, payment_data)
                    self.assertEqual(response.status_code, 200)

                    self.assertEqual(AimerMember.objects.count(), 1)
                    aimer_member = AimerMember.objects.get(participant=participant)
                    self.assertEqual(aimer_member.participant, participant)
                    self.assertTrue(aimer_member.is_active_member)
                    updated_registration = ParticipantRegistration.objects.last()
                    self.assertEqual(updated_registration.razorpay_payment_id, 'pay_test')
                    self.assertEqual(updated_registration.payment_status, True)
                    self.assertEqual(updated_registration.amount_paid, 2000)
                    self.assertIsInstance(updated_registration.registered_at, datetime.datetime)

    def test_register_for_workshop(self):
        participant_data = {
            "name": "Test User",
            "email": "test_workshop@example.com",
            "mobile_number": "1234567890",
            "registration_type": self.workshop_type.id
        }
        with patch('registration.views.client') as mock_client:
            mock_client.order.create.return_value = {
                'id': 'test_order_id',
                'receipt': f"order_rcptid_1",
                'amount': self.workshop_pricing.early_bird_price  # Use early bird price for workshop
            }
            response = self.client.post(self.registration_url, participant_data)

            self.assertEqual(response.status_code, 200)  # Expecting a redirect

            participant = Participant.objects.get(email="test_workshop@example.com")
            self.assertEqual(ParticipantRegistration.objects.count(), 1)
            self.assertEqual(AimerMember.objects.count(), 0)  # No AimerMember creation for workshops

            registration = ParticipantRegistration.objects.last()
            self.assertEqual(registration.registration_type, self.workshop_type)
            self.assertNotEqual(registration.amount_paid, self.workshop_pricing.early_bird_price)  # Not paid yet

            payment_data = {
                'razorpay_payment_id': "pay_test",
                'razorpay_order_id': 'test_order_id',
                'razorpay_signature': 'test_signature'
            }

            with patch('registration.views.client.utility.verify_payment_signature') as mock_verify_signature:
                with patch('registration.views.client.order.fetch') as mock_order_fetch:
                    mock_order_fetch.return_value = {
                            'id': 'test_order_id',
                            'entity': 'order',
                            'amount': self.workshop_pricing.early_bird_price * 100,  # Match workshop pricing
                            'amount_paid': self.workshop_pricing.early_bird_price * 100,
                            'amount_due': 0,
                            'currency': 'INR',
                            'receipt': 'order_rcptid_1',
                            'offer_id': None,
                            'status': 'paid',
                            'attempts': 1,
                            'notes': [],
                            'created_at': 1737564274
                    }

                    mock_verify_signature.return_value = None

                    response = self.client.post(self.payment_success_url, payment_data)
                    self.assertEqual(response.status_code, 200)

                    self.assertEqual(AimerMember.objects.count(), 0)  # No AimerMember creation for workshops
                    registration = ParticipantRegistration.objects.last()
                    self.assertEqual(registration.razorpay_payment_id, 'pay_test')
                    self.assertEqual(registration.payment_status, True)
                    self.assertEqual(registration.amount_paid, self.workshop_pricing.early_bird_price)
                    self.assertIsInstance(registration.registered_at, datetime.datetime)