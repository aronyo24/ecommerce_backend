from rest_framework import serializers

class CreatePaymentIntentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    provider = serializers.ChoiceField(choices=['stripe', 'bkash'], default='stripe')
