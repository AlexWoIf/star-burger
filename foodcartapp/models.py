from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from geopoints.models import Geopoint


class OrderQuerySet(models.QuerySet):
    def fetch_with_total(self):
        fetch_with_total = self.annotate(total=Sum('products__price'))
        return fetch_with_total

    def fetch_with_coordinates(self):
        for order in self:
            geopoint, _ = Geopoint.objects.get_or_create(
                address=order.address,
            )
            order.lat = geopoint.lat
            order.lon = geopoint.lon
        return self


class RestaurantQuerySet(models.QuerySet):
    def fetch_with_coordinates(self):
        for restaurant in self:
            geopoint, _ = Geopoint.objects.get_or_create(
                address=restaurant.address,
            )
            restaurant.lat = geopoint.lat
            restaurant.lon = geopoint.lon
        return self


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=200,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    objects = RestaurantQuerySet.as_manager()

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
        ('10_N', 'New'),
        ('20_C', 'Check data'),
        ('30_M', 'Cook and pack'),
        ('40_D', 'Delivering'),
        ('50_F', 'Finished'),
    ]
    PAYMENT_CHOICES = [
        ('D', 'Наличными при доставке'),
        ('B', 'Накопленными бонусами/скидками'),
        ('O', 'Картой онлайн'),
    ]
    firstname = models.CharField('Имя', blank=True, max_length=200, default='')
    lastname = models.CharField('Фамилия', blank=True, max_length=200,
                                default='')
    phonenumber = PhoneNumberField('Телефон заказчика ',
                                   db_index=True, )
    address = models.CharField('Адрес доставки', max_length=200, )
    status = models.CharField('статус', max_length=5, choices=STATUS_CHOICES,
                              default='10_N', db_index=True, )
    payment = models.CharField('Способ оплаты', max_length=2,
                               choices=PAYMENT_CHOICES, blank=True, default='',
                               db_index=True, )
    comment = models.TextField('комментарий', blank=True, default='')
    created_at = models.DateTimeField('Время создания', default=timezone.now,
                                      db_index=True, )
    called_at = models.DateTimeField('Время звонка', null=True, blank=True,
                                     db_index=True, )
    delivered_at = models.DateTimeField('Время доставки', null=True,
                                        blank=True, db_index=True, )
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE,
                                   related_name='orders', null=True,
                                   verbose_name='Ресторан', blank=True, )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.phonenumber}"

    def get_available_restaurant(self):
        order_items = self.products.all()
        available_restaurants = Restaurant.objects.filter(
                menu_items__product__in=[
                    *order_items.values_list('product__pk', flat=True)
                ]
            ).annotate(count=Count('menu_items__product')).filter(
                count=order_items.count()
            )
        return available_restaurants


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
