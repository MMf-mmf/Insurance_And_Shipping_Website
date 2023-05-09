from django.urls import path, re_path
from . import views 
from . import webhooks
# instantiate python date object with date 2000-01-01
# from datetime import date
# from django.utils import timezone
# from django.contrib.auth.decorators import login_required


 
app_name = 'payments_app'

process_payment = [
    path('checkout/<uuid:file_id>/', views.Checkout.as_view(), name='checkout'),
    # path('submit_order/', views.submit_order, name='submit_order'),
]

indirect_post_payment = [
    path('payment_complete/<uuid:order_id>/', views.payment_complete, name='payment_complete'),
    path('payment_canceled/<uuid:file_id>/', views.payment_canceled, name='payment_canceled'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook'), # for stripe to tell us that a payment was successful or not
    # path('intuit/webhook/', webhooks.intuit_webhook, name='intuit_webhook'), # for intuit to tell us that a payment was successful or not
    # path('intuit_redirect/', views.intuit_redirect, name='intuit_redirect'), # this is a redirect url to send auth tokens
]


urlpatterns = [
   *process_payment,
   *indirect_post_payment,
]


