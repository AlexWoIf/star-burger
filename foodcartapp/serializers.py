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

    def create(self, validated_data):
        return OrderItem.objects.create(**validated_data)


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, )
    total = serializers.DecimalField(max_digits=8, decimal_places=2,
                                     default=0, read_only=True, )
    status_display = serializers.CharField(source='get_status_display',
                                           allow_blank=True, read_only=True, )
    payment_display = serializers.CharField(source='get_payment_display',
                                            allow_blank=True, read_only=True, )

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'status_display',
                  'phonenumber', 'address', 'products', 'total', 'comment',
                  'payment_display', 'restaurant', ]

    def create(self, validated_data):
        order_data = dict(validated_data)
        products = order_data.pop('products')
        order = Order.objects.create(**order_data)
        for item in products:
            item['price'] = item['product'].price * item['quantity']
            item['product'] = item['product'].id
            item_serializer = OrderItemSerializer(data=item)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.validated_data['order'] = order
            item_serializer.create(item_serializer.validated_data)
        return order
