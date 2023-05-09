from payments_app.models import Order, OrderItem, AccountCredit, SpentCreditHistory
from utils.email_sender import send_order_confirmation_email
from django.db import transaction
import pandas as pd
from ..webhooks import add_shipments_to_master_file_and_calculate_credits

@transaction.atomic # this function will create a order and order items in a single transaction
def create_order_and_items(request, form, shipment_file, file_id, credit=0):
    try:
        order = Order.objects.filter(shipment_file__id=file_id)
        
        if order.exists():
            return order.first()
        else:
            order = form.save()
            
            order.total_cost = str(shipment_file.price)
            order.shipment_file = shipment_file # since the order is initially created by the form and the form douse not have the file attached, we must do it now
            order.total_shipments = shipment_file.total_shipments
            order.discount_applied = credit
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            # first read the file to get the data we need for the order items
            try:
                uploaded_df = pd.read_csv(shipment_file.file)
                carrier_services = uploaded_df['ShippingMethodSelected'].value_counts()
                for service_name, count in carrier_services.items():
                    # get the total price/cost of all the shipments with a given carrier service
                    price = uploaded_df[uploaded_df['ShippingMethodSelected'] == service_name].Price.values.sum()
                    OrderItem.objects.create(
                        order = order,
                        shipping_service = service_name,
                        quantity = count,
                        price = price,
                    )
                return order
            except Exception as e:
                print(e)
                return None
        
    except Exception as e:
        print(e)
        return None
    
def complete_order_and_deduct_credit(order, shipment_file):
    order.paid = True
    order.save()
    file_path = shipment_file.file.path
    shipment_file.in_cart = False
    shipment_file.save()
    # send email to the user
    send_order_confirmation_email(order, file_path)
    
    # deduct the credit just used
    user = order.user
    credit_used = order.discount_applied
    account_credit = AccountCredit.objects.get(user=user)
    account_credit.credit_amount -= credit_used
    account_credit.save()
    # create a SpentCreditHistory object
    SpentCreditHistory.objects.create(
        account_credit = account_credit,
        amount_used = credit_used,
        note = f'Credit for order {order.id}'
    )
    add_shipments_to_master_file_and_calculate_credits(order, file_path, user)
