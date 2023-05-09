from django.views.generic import View
from django.urls import reverse
from payments_app.models import Order, OrderItem, AddedCreditHistory, AccountCredit
from users_app.models import Profile
from pricing_app.models import ShipmentFile
from decimal import Decimal
import stripe
from django.conf import settings
from .forms import OrderForm
from django.shortcuts import render, redirect, get_object_or_404, reverse
# from .quickbooks_helpers import refresh_tokens, get_tokens, create_invoice
from django.contrib import messages
from .services.general_services import create_order_and_items, complete_order_and_deduct_credit
from django.http import HttpResponse
from django.utils import timezone
from utils.email_sender import send_refund_email, dev_alert_email


class Checkout(View):
    def get(self, request, file_id):
        if request.user.is_authenticated:
            # get the price from ShipmentFile
            order_total = ShipmentFile.objects.get(id=file_id).price
            # try to get the credit amount from AccountCredit
            try:
                credit = AccountCredit.objects.get(user=request.user).credit_amount
            except AccountCredit.DoesNotExist:
                # sent dev email that a user was created and the sign up signal did not create an AccountCredit object
                dev_alert_email(AccountCredit, error='AccountCredit object does not exist for user', user=request.user)
                # create an AccountCredit object for the user
                account_credit = AccountCredit.objects.create(user=request.user)
                credit = account_credit.credit_amount
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                dev_alert_email(AccountCredit, error='AccountCredit object does not exist for user', user=request.user)
                profile = Profile.objects.create(user=request.user)
                
            form = OrderForm(
                credit=credit,
                order_total=order_total,
                initial={'first_name': profile.first_name, 'last_name': profile.last_name, 'email': profile.email, 'address': profile.address, 'postal_code': profile.postal_code, 'city': profile.city}
                )
        else:
            form = OrderForm()
            credit = None
        
        return render(request, "checkout.html", {'profile_form': form,'file_id': file_id, 'credit': credit, 'order_total': order_total})

  
    def post(self, request, file_id):
        order_total = ShipmentFile.objects.get(id=file_id).price
        credit = AccountCredit.objects.get(user=request.user).credit_amount
        form = OrderForm(request.POST, credit=credit, order_total=order_total,)
        discount_value = Decimal(0) # default value

        if form.is_valid():
            shipment_file = ShipmentFile.objects.filter(id=file_id)
            # test if the discount_applied field exists in the form
            if 'discount_applied' in form.cleaned_data:
                applied_credit = form.cleaned_data['discount_applied']
            else:
                applied_credit = Decimal(0)
            if shipment_file.exists():
                shipment_file = shipment_file.first()
            else:
                messages.error(request, 'File not found', extra_tags='error')
                return render(request, "checkout.html", {'profile_form': form,'file_id': file_id})
            
                        
            # if the user is paying the full amount with credit handle the order here
             # establish the discount value
            if applied_credit == order_total and credit >= applied_credit:
                discount_value = applied_credit
                order = create_order_and_items(request, form, shipment_file, file_id, credit=discount_value)
                # if order was created successfully
                if order is not None:
                    complete_order_and_deduct_credit(order, shipment_file)
                    
                    return redirect('payments_app:payment_complete', order_id=order.id)
                else:
                    messages.error(request, 'Something went wrong, please try again', extra_tags='error')
                    return redirect('payments_app:payment_canceled', file_id=file_id)
            
            
            # establish the discount value
            if applied_credit > 0 and credit >= applied_credit:
                discount_value = applied_credit
            # create order in database if not yet done
            order = create_order_and_items(request, form, shipment_file, file_id, credit=discount_value)
            order_id = order.id
            
            # create the stripe instance
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.api_version = settings.STRIPE_API_VERSION
            # create a stripe payment session store it and redirect to stripe
            
            success_url = request.build_absolute_uri(reverse('payments_app:payment_complete', kwargs={'order_id':order_id}))
            cancel_url = request.build_absolute_uri(reverse('payments_app:payment_canceled', kwargs={'file_id':file_id}))

            # Stripe Checkout Session Data
            session_data = {
                'mode': 'payment',
                'client_reference_id': order.id,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'customer_email':  order.email,
                'line_items': [{
                        'price_data': {
                            'unit_amount': int(shipment_file.price *  Decimal('100') - (discount_value * Decimal(100))),
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Shipping Insurance'
                            },
                        },
                        'quantity': 1,  
                }],
               'payment_method_types': ['card', 'us_bank_account'],
            }
          
            # Create the session
            session = stripe.checkout.Session.create(**session_data)
            
            return redirect(session.url, code=303)
        return render(request, "checkout.html", {'file_id': file_id})
           
    

def payment_complete(request, order_id):
    return render(request, "payment_complete.html", {'order_id': order_id})

def payment_canceled(request, file_id):
    # delete the order and display a link to go back to the checkout page
    return render(request, "payment_canceled.html", {'file_id': str(file_id)})


def refund_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    response = stripe.Refund.create(
    payment_intent=order.stripe_payment_intent,
    reason='requested_by_customer',
    )
    if response.status == 'succeeded':
        # store the refund id in the order model
        order.stripe_id = response.id
        order.refund_date = timezone.now()
        order.save()
        send_refund_email(order)
        messages.success(request, 'Refund was successful', extra_tags='success')
        return HttpResponse(status=200)
    else:
        messages.error(request, 'Unable to Refund purchase', extra_tags='error')
        return HttpResponse(status=400)






################## Quick books ############################
# def submit_order(request):
#     # create a Order and orderItems out of the shipments
    
#     # create a invoice in quickbooks and each of the items will be a line on the invoice
    
#     # send a email that the order was created and you will get you invoice with a payment link by the end of the week
#     breakpoint()
#     pass

# def intuit_redirect(request):
#     auth_code = request.GET.get('code')
#     realm_id = request.GET.get('realmId')
#     access_token = get_tokens(request, auth_code, realm_id)

#     messages.success(request, 'File Uploaded Successfully', extra_tags='success')
#     redirect('home') # for now just go to the home page
    
# def proses_payment_with_stripe(self, request, file_id):  
#     form = OrderForm(request.POST)
#     # if form is valid
#     if form.is_valid():
#         # create a Order object and return the order id
#         order = form.save()
        
#         # create a OrderItem object
#         # for now we are working with one item in the future we will have multiple items/multiple files
#         shipment_file = get_object_or_404(ShipmentFile, id=file_id)
#         OrderItem.objects.create(order=order, shipment_file=shipment_file)
        
#         # create the stripe instance
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         stripe.api_version = settings.STRIPE_API_VERSION
#         # create a stripe payment session store it and redirect to stripe
#         success_url = request.build_absolute_uri(reverse('payments_app:payment_complete', kwargs={'order_id':order.id}))
#         cancel_url = request.build_absolute_uri(reverse('payments_app:payment_canceled', kwargs={'file_id':file_id}))

#         # Stripe Checkout Session Data
#         session_data = {
#             'mode': 'payment',
#             'client_reference_id': order.id,
#             'success_url': success_url,
#             'cancel_url': cancel_url,
#             'line_items': [{
#                     'price_data': {
#                         'unit_amount': int(shipment_file.price *  Decimal('100')),
#                         'currency': 'usd',
#                         'product_data': {
#                             'name': 'Shipping Insurance'
#                         },
#                     },
#                     'quantity': 1,  
#             }],
#         }
#         # WHEN WE HAVE ALL THE SHIPMENTS CATEGORIZED BY CARRIER SERVICE WE CAN DO SOMETHING LIKE THIS TO ADD EVERY SHIPPING SERVICE AS ITS OWN ITEM WITH A PRICE AND QUANTITY
#         # for item in order.items.all():
#         # session_data['line_items'].append({
#         #     'price_data': {
#         #         'unit_amount': int(item.price * Decimal('100')),
#         #         'currency': 'usd',
#         #         'product_data': {
#         #             'name': item.product.name,
#         #         },
#         #     },
#         #     'quantity': item.quantity,
#         # })
#         # Create the session
#         session = stripe.checkout.Session.create(**session_data)
        
#         return redirect(session.url, code=303)
#     return render(request, "checkout.html", {'file_id': file_id})