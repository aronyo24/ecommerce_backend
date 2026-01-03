from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from rest_framework_api_key.models import APIKey
from unittest.mock import patch

User = get_user_model()

class PaymentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.order = Order.objects.create(
            user=self.user,
            total=100.00,
            street='123 Main St',
            city='City',
            state='State',
            zip_code='12345',
            country='Country'
        )
        self.api_key, self.key = APIKey.objects.create_key(name="Test Key")

    @patch('apps.payments.services.stripe.StripeProvider.create_payment_intent')
    def test_create_payment_intent_with_api_key(self, mock_create_intent):
        mock_create_intent.return_value = {
            'id': 'pi_123',
            'client_secret': 'secret',
            'status': 'pending'
        }
        
        # Use API Key header
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key}')
        
        data = {'order_id': str(self.order.id)}
        response = self.client.post('/api/payments/create-payment-intent/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'pi_123')

    @patch('apps.payments.services.stripe.StripeProvider.create_payment_intent')
    def test_create_payment_intent_without_auth(self, mock_create_intent):
        self.client.credentials() # No auth
        data = {'order_id': str(self.order.id)}
        response = self.client.post('/api/payments/create-payment-intent/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.payments.services.bkash.BkashProvider.create_payment_intent')
    def test_create_payment_intent_bkash(self, mock_create_intent):
        mock_create_intent.return_value = {
            'id': 'bkash_123',
            'payment_url': 'http://bkash.com/pay',
            'status': 'pending'
        }
        
        self.client.force_authenticate(user=self.user)
        data = {'order_id': str(self.order.id), 'provider': 'bkash'}
        response = self.client.post('/api/payments/create-payment-intent/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 'bkash_123')
        self.assertEqual(response.data['payment_url'], 'http://bkash.com/pay')
