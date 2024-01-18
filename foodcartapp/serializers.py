from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Order, OrderItem, Restaurant


class RestaurantSerializer(ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ['id', 'name',]


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', ]


class RegisterOrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, )
    total = serializers.DecimalField(max_digits=8, decimal_places=2,
                                     default=0, )

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'phonenumber', 'address', 'products', 'total', 'comment', ]


class ListOrderSerializer(ModelSerializer):
    restaurant = RestaurantSerializer(allow_null=True)
    total = serializers.DecimalField(max_digits=8, decimal_places=2,
                                     default=0, )
    status_display = serializers.CharField(source='get_status_display',
                                           allow_blank=True, )
    payment_display = serializers.CharField(source='get_payment_display',
                                            allow_blank=True, )

    class Meta:
        model = Order
        fields = ['id', 'status_display', 'firstname', 'lastname',
                  'phonenumber', 'address', 'total', 'comment',
                  'payment_display', 'restaurant', ]
