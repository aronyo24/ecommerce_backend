from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.orders.models import Order
from .models import Payment
from .services.stripe import StripeProvider
from .services.bkash import BkashProvider
from .serializers import CreatePaymentIntentSerializer
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated

class CreatePaymentIntentView(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            
            if request.user.is_authenticated:
                order = get_object_or_404(Order, id=order_id, user=request.user)
                user = request.user
            else:
                # API Key access
                order = get_object_or_404(Order, id=order_id)
                user = order.user
            
            # Check if payment already exists and is successful
            if order.payment_status == 'success':
                return Response({'error': 'Order already paid'}, status=status.HTTP_400_BAD_REQUEST)

            provider_name = serializer.validated_data.get('provider', 'stripe')
            
            if provider_name == 'bkash':
                provider = BkashProvider()
                currency = 'BDT'
            else:
                provider = StripeProvider()
                currency = 'usd'

            try:
                # Create Payment Intent
                intent_data = provider.create_payment_intent(
                    amount=order.total,
                    currency=currency,
                    metadata={'order_id': str(order.id)}
                )
                
                # Create Payment record
                Payment.objects.create(
                    order=order,
                    user=user,
                    amount=order.total,
                    provider=provider_name,
                    transaction_id=intent_data['id'],
                    status='pending',
                    raw_response=intent_data
                )
                
                return Response(intent_data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_success(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_payment_failure(payment_intent)

        return Response(status=status.HTTP_200_OK)

    def handle_payment_success(self, payment_intent):
        order_id = payment_intent['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'success'
                order.status = 'processing' # Or whatever next status
                order.transaction_id = payment_intent['id']
                order.save()
                
                # Update Payment record
                payment = Payment.objects.filter(transaction_id=payment_intent['id']).first()
                if payment:
                    payment.status = 'success'
                    payment.raw_response = payment_intent
                    payment.save()
            except Order.DoesNotExist:
                pass

    def handle_payment_failure(self, payment_intent):
        order_id = payment_intent['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'failed'
                order.save()
            except Order.DoesNotExist:
                pass

@method_decorator(csrf_exempt, name='dispatch')
class BkashWebhookView(APIView):
    def post(self, request):
        # Placeholder for bKash webhook
        # Implement signature verification and status updates here
        return Response(status=status.HTTP_200_OK)

class ConfirmPaymentView(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        provider_name = request.data.get('provider', 'stripe') # Default to stripe for backward compatibility

        if not payment_intent_id:
             return Response({'error': 'payment_intent_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find existing payment record to determine provider
        payment = Payment.objects.filter(transaction_id=payment_intent_id).first()
        if payment:
            provider_name = payment.provider
        
        try:
            if provider_name == 'bkash':
                provider = BkashProvider()
                # Confirm (Execute) Payment
                result = provider.confirm_payment(payment_intent_id)
                
                # Update Order and Payment
                if result['status'] == 'succeeded':
                    if payment:
                        order = payment.order
                        order.payment_status = 'success'
                        order.status = 'processing'
                        order.transaction_id = result['transaction_id']
                        order.save()
                        
                        payment.status = 'success'
                        # Keep transaction_id as paymentID for bKash to allow lookups/idempotency
                        # payment.transaction_id = result['transaction_id'] 
                        payment.raw_response = result['raw_response']
                        payment.save()
                        
                        return Response({'status': 'success', 'order_id': order.id})
                    else:
                         # Should not happen if flow is correct, but handle just in case
                         return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'status': 'failed', 'details': result})

            else:
                # Stripe Logic
                stripe.api_key = settings.STRIPE_SECRET_KEY
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                
                if intent.status == 'succeeded':
                    order_id = intent.metadata.get('order_id')
                    if order_id:
                        order = get_object_or_404(Order, id=order_id)
                        
                        # Update Order
                        if order.payment_status != 'success':
                            order.payment_status = 'success'
                            order.status = 'processing'
                            order.transaction_id = intent.id
                            order.save()
                            
                            # Update Payment record
                            if payment:
                                payment.status = 'success'
                                payment.raw_response = intent
                                payment.save()
                            else:
                                 # Create if not exists (edge case)
                                 Payment.objects.create(
                                    order=order,
                                    user=order.user,
                                    amount=order.total,
                                    provider='stripe',
                                    transaction_id=intent.id,
                                    status='success',
                                    raw_response=intent
                                )
                        
                        return Response({'status': 'success', 'order_id': order.id})
                
                return Response({'status': intent.status})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

