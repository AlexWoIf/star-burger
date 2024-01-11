from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class OrderQuerySet(models.QuerySet):
    def fetch_with_total(self):
        fetch_with_total = self.annotate(total=Sum('products__price'))
        return fetch_with_total


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=255,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('N', 'New'),
        ('C', 'Check data'),
        ('M', 'Cook and pack'),
        ('D', 'Delivering'),
        ('F', 'Finished'),
    ]
    firstname = models.CharField('Имя', blank=True, max_length=200, )
    lastname = models.CharField('Фамилия', blank=True, max_length=200, )
    phonenumber = PhoneNumberField(
                        'Телефон заказчика ',
                        db_index=True,
                    )
    address = models.CharField('Адрес доставки', max_length=200, )
    objects = OrderQuerySet.as_manager()
    status = models.CharField(
        'статус',
        max_length=2,
        choices=STATUS_CHOICES,
        default='N',
        db_index=True
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.phonenumber}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ',
                              related_name='products',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Продукт',
                                related_name='ordered',
                                on_delete=models.CASCADE)
    quantity = models.IntegerField('Количество', )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', ]


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, )
    total = serializers.DecimalField(
                                max_digits=8,
                                decimal_places=2,
                                default=0, )
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = ['id', 'status_display', 'firstname', 'lastname',
                  'phonenumber', 'address', 'products', 'total', ]
