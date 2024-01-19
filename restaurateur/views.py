from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Order, Product, Restaurant
from foodcartapp.serializers import OrderSerializer, RestaurantSerializer


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability
                        for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False)
                                for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability':
            products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = list(Order.objects.prefetch_related('products')
                  .select_related('restaurant').fetch_with_total()
                  .exclude(status='F')
                  .fetch_with_coordinates())
    choices = {
        choice_id: position for position, (choice_id, _) in
        enumerate(Order.STATUS_CHOICES)
    }
    orders.sort(key=lambda order: choices[order.status])
    context = {'orders': [], }
    for order in orders:
        serialized_order = OrderSerializer(order).data
        if order.restaurant is None:
            available_restaurants = [*order.get_available_restaurant()
                                     .fetch_with_coordinates()]
            serialized_order['restaurants'] = []
            for restaurant in available_restaurants:
                serialized_restaurant = RestaurantSerializer(restaurant).data
                if (
                    restaurant.lat is None or restaurant.lon is None or
                    order.lat is None or order.lon is None
                ):
                    serialized_restaurant['distance'] = None
                else:
                    serialized_restaurant['distance'] = round(
                        distance.distance((order.lat, order.lon),
                                          (restaurant.lat, restaurant.lon)).km
                    )
                serialized_order['restaurants'].append(serialized_restaurant)
            serialized_order['restaurants'].sort(
                key=lambda el: (el['distance'] is None, el['distance'])
            )
        context['orders'].append(serialized_order)
    return render(request, template_name='order_list.html', context=context)
