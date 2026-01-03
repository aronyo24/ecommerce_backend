import stripe

from django.conf import settings
from .base import PaymentProvider

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeProvider(PaymentProvider):
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        try:
            # Stripe expects amount in cents
            amount_cents = int(amount * 100)
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                'client_secret': intent.client_secret,
                'id': intent.id,
                'status': intent.status
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    def confirm_payment(self, payment_intent_id):
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
