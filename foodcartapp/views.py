from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product, OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST',])
def register_order(request):
    serialized_order = OrderSerializer(data=request.data)
    serialized_order.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serialized_order.validated_data['firstname'],
        lastname=serialized_order.validated_data['lastname'],
        phonenumber=serialized_order.validated_data['phonenumber'],
        address=serialized_order.validated_data['address']
    )
    order_items = serialized_order.validated_data['products']
    products = [OrderItem(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price*item['quantity'],
                ) for item in order_items]
    OrderItem.objects.bulk_create(products)
    order.total = sum([product.price for product in products])
    serialized_order = OrderSerializer(order)
    return Response({'status': 'ok',
                     'order': serialized_order.data, },
                    status=status.HTTP_201_CREATED, )
