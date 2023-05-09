from django.urls import path, re_path
from .views import ShippingQuoteView


urlpatterns = [
    path('shipping_quote/', ShippingQuoteView.as_view(), name='shipping_quote'),
]