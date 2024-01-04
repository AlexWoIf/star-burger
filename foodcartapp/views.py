from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from pydantic import BaseModel, ValidationError, conlist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product


class ItemSchema(BaseModel):
    product: int
    quantity: int


class OrderSchema(BaseModel):
    firstname: str
    lastname: str
    phonenumber: str
    address: str
    products: conlist(ItemSchema, min_length=1)


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
    try:
        print(request.data)
        order_payload = OrderSchema(**request.data)
    except ValidationError as error:
        return Response({'error': str(error), },
                        status=status.HTTP_406_NOT_ACCEPTABLE )
    order = Order.objects.create(
        firstname=order_payload.firstname,
        lastname=order_payload.lastname,
        phonenumber=order_payload.phonenumber,
        address=order_payload.address
    )
    products = order_payload.products
    for product in products:
        OrderItem.objects.create(
            order=order,
            product=get_object_or_404(Product,  pk=product.product, ),
            quantity=product.quantity
        )
    return JsonResponse({'status': 200}, safe=False, )
