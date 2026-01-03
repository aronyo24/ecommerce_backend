from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'product_image', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    # CamelCase for frontend
    userId = serializers.ReadOnlyField(source='user.id')
    paymentProvider = serializers.CharField(source='payment_provider')
    paymentStatus = serializers.CharField(source='payment_status', read_only=True)
    transactionId = serializers.CharField(source='transaction_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    # Flat address fields to nested object for frontend
    shippingAddress = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'userId', 'items', 'total', 'status', 
            'paymentProvider', 'paymentStatus', 'transactionId', 
            'shippingAddress', 'createdAt', 'updatedAt'
        ]

    def get_shippingAddress(self, obj):
        return {
            'street': obj.street,
            'city': obj.city,
            'state': obj.state,
            'zip': obj.zip_code,
            'country': obj.country,
        }

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    # Frontend sends shippingAddress as an object
    shippingAddress = serializers.JSONField(write_only=True)
    paymentProvider = serializers.CharField(source='payment_provider')

    class Meta:
        model = Order
        fields = ['items', 'total', 'paymentProvider', 'shippingAddress']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        shipping_address = validated_data.pop('shippingAddress')
        
        # Extract individual address fields
        validated_data['street'] = shipping_address.get('street')
        validated_data['city'] = shipping_address.get('city')
        validated_data['state'] = shipping_address.get('state')
        validated_data['zip_code'] = shipping_address.get('zip')
        validated_data['country'] = shipping_address.get('country')
        
        order = Order.objects.create(user=self.context['request'].user, **validated_data)
        
        for item_data in items_data:
            product = item_data.get('product')
            if product:
                # Basic stock reduction
                if product.stock >= item_data['quantity']:
                    product.stock -= item_data['quantity']
                    product.save()
            OrderItem.objects.create(order=order, **item_data)
            
        return order

