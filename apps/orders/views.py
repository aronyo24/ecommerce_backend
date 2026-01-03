from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # After saving, return the full serialized order
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

