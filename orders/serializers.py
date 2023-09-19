from rest_framework import serializers
from .models import Order, OrderToken
from users.serializers import UserSerializer


class OrderTokenSerializer(serializers.ModelSerializer):
    """
    Order Token Serializer
    """
    class Meta:
        model = OrderToken
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """
    Order Serializer
    """
    order_tokens = OrderTokenSerializer(many=True, required=False, partial=True)
    buyer = UserSerializer(many=False, required=False, partial=True)

    class Meta:
        model = Order
        fields = '__all__'