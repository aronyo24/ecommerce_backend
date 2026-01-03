from .base import PaymentProvider
import requests
import json
from django.conf import settings
import uuid
import time

class BkashProvider(PaymentProvider):
    def __init__(self):
        self.base_url = settings.BKASH_BASE_URL
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'username': self.username,
            'password': self.password
        }

    def _get_token(self):
        url = f"{self.base_url}/tokenized/checkout/token/grant"
        payload = {
            "app_key": self.app_key,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('id_token')
        except requests.exceptions.RequestException as e:
            raise Exception(f"bKash Token Error: {str(e)}")

    def create_payment_intent(self, amount, currency='BDT', metadata=None):
        token = self._get_token()
        if not token:
            raise Exception("Failed to get bKash token")

        url = f"{self.base_url}/tokenized/checkout/create"
        
        # Ensure metadata exists
        metadata = metadata or {}
        order_id = metadata.get('order_id', str(uuid.uuid4()))
        
        # Append timestamp to make invoice number unique for each attempt
        # This prevents "Duplicate Invoice" errors if the user retries payment
        invoice_number = f"{order_id}_{int(time.time())}"
        
        headers = {
            'Authorization': token,
            'X-APP-Key': self.app_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "mode": "0011",
            "payerReference": "01711111111", # Sandbox requirement or user phone
            "callbackURL": "http://localhost:8080/payment/bkash/callback", # Frontend callback
            "amount": str(amount),
            "currency": currency,
            "intent": "sale",
            "merchantInvoiceNumber": invoice_number
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('statusCode') != '0000':
                 raise Exception(f"bKash Create Error: {data.get('statusMessage')}")

            return {
                'client_secret': token, # Storing token as client_secret for reuse if needed
                'id': data.get('paymentID'),
                'status': 'pending',
                'payment_url': data.get('bkashURL'),
                'raw_response': data
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"bKash Create Request Error: {str(e)}")

    def confirm_payment(self, payment_intent_id):
        # For bKash, confirmation usually happens via Execute API after user interaction
        # This method might be called with the paymentID
        
        # We need the token again. In a real app, we might cache it.
        token = self._get_token()
        
        url = f"{self.base_url}/tokenized/checkout/execute"
        
        headers = {
            'Authorization': token,
            'X-APP-Key': self.app_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "paymentID": payment_intent_id
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('statusCode') != '0000':
                 raise Exception(f"bKash Execute Error: {data.get('statusMessage')}")

            return {
                'id': data.get('paymentID'),
                'status': 'succeeded', # Mapped to our internal status
                'transaction_id': data.get('trxID'),
                'raw_response': data
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"bKash Execute Request Error: {str(e)}")

