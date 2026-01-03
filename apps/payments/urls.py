from django.urls import path
from .views import CreatePaymentIntentView, StripeWebhookView, ConfirmPaymentView, BkashWebhookView

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('webhook/bkash/', BkashWebhookView.as_view(), name='bkash-webhook'),
]
