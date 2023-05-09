from django.urls import path, re_path
from .views import (ProfileView, OrderDetailView,
                    ShoppingCartView, ContactUsView,
                    add_to_cart,
                    email_terms_and_conditions,)


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/order_detail/<uuid:file_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('shopping_cart/', ShoppingCartView.as_view(), name='shopping_cart'),
    path('add_to_cart/<uuid:file_id>/', add_to_cart, name='add_to_cart'),
    path('contact_us/', ContactUsView.as_view(), name='contact_us'),
    path('email_terms_and_conditions/', email_terms_and_conditions, name='email_terms_and_conditions'),
]
