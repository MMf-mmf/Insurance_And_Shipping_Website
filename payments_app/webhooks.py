import pandas as pd
import chardet
import stripe
from google.cloud import storage
from decimal import Decimal
from django.db.models import Sum
from django.core.files import File
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Order
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from pricing_app.models import ShipmentFile, RateCard, RateCardItem
from payments_app.models import InsuredShipments, AddedCreditHistory, AccountCredit, SpentCreditHistory
from utils.helper_functions import get_object_or_email_alert
from django.utils import timezone
from utils.email_sender import general_dev_alert_email, send_order_confirmation_email





@csrf_exempt # this request is coming from stripe and not from our server so it will not have a csrf token
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
                )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # invalid signature
        return HttpResponse(status=400)

    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            order = get_object_or_email_alert(Order, id=session.client_reference_id)
            file = get_object_or_email_alert(ShipmentFile, id=str(order.shipment_file.id))
            user = order.user
            # UPDATE THE ORDER MODEL
            order.paid = True
            order.stripe_payment_intent = session.payment_intent
            order.save()
            # get file to send in email
            # file_path = order.shipment_file.file
            # UPDATE THE SHIPMENT FILE MODEL
            file.in_cart = False
            file.save()
            # if the order used a discount deduct that from the users account
            
            if order.discount_applied > 0:
                credit_used = order.discount_applied
                account_credit = AccountCredit.objects.get(user=user)
                account_credit.credit_amount -= credit_used
                account_credit.save()
                # create a SpentCreditHistory object
                spend_history = SpentCreditHistory.objects.create(
                    account_credit = account_credit,
                    amount_used = credit_used,
                    note = f'Credit for order {order.id}'
                )
            send_order_confirmation_email(order, file)
            add_shipments_to_master_file_and_calculate_credits(order, file, user)
    return HttpResponse(status=200)



def add_shipments_to_master_file_and_calculate_credits(order, file, user):
    """ADD SHIPMENTS TO THE USERS MONTHLY FILE, FOR THE PURPOSE OF CALCULATING EVALUATING IF A USER QUALIFIES FRO A DISCOUNT THIS MONTH, THROW SPENDING ENOUGH TO QUALIFY FOR A HIRE TIER RATE CARD"""
    if order.user:
        master_file = InsuredShipments.objects.filter(user=user, created__month=timezone.now().month)
        
        try:
            if master_file.exists(): # grab the file with the past shipments and append the newly insured shipments to it
                master_file = master_file.first()
                # READ THE FILES 
                file.file.open()
                file_string_byt = file.file.read()
                master_file_string_byt = master_file.file.file.read()
                # CONVERT THE BYTES TO STRINGS
                uploaded_file_encoding = chardet.detect(file_string_byt)['encoding']
                master_file_encoding = chardet.detect(master_file_string_byt)['encoding']
                file_string_string = file_string_byt.decode(uploaded_file_encoding)
                master_file_string_string = master_file_string_byt.decode(master_file_encoding)
                # REMOVE THE HEADERS FROM THE PURCHASED SHIPMENT FILE
                file_string_with_removed_headers = file_string_string.splitlines()[1:]
                # NOW PUT THE STRING BACK TOGETHER WITH A NEW LINE AFTER EACH LINE
                file_string_with_removed_headers = '\n'.join(file_string_with_removed_headers)
                # DO A SIMILAR PROCESS FOR THE MASTER ONLY NO HEADERS ARE REMOVED ITS JUST TO KEEP BOTH FILES IN THE SAME FORMAT WITH ONE NEW LINE AFTER EACH LINE
                master_file_string_string = master_file_string_string.splitlines()
                master_file_string_string = '\n'.join(master_file_string_string)
                # NOW CONCATENATE THE TWO FILES        
                new_master_file_string_string = master_file_string_string + '\n' + file_string_with_removed_headers
                # NOW WRITE THE NEW FILE TO THE BUCKET THIS WILL OVERWRITE THE OLD FILE
                client = storage.Client.from_service_account_json(settings.GOOGLE_JSON_FILE)
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob(master_file.file.name)
                with blob.open('w') as f:
                    f.write(new_master_file_string_string)
                file.file.close()
            else: # create a new file and add the full content of the file to it
              
                file.file.open()
                file_string_bytes = file.file.read()
                master_file = InsuredShipments.objects.create(user=user)
                file_name =  f'{user.username}_{timezone.now().month}_{timezone.now().year}.csv'
                master_file.file.save(file_name, ContentFile(file_string_bytes))
                file.file.close()
            print('made it passed the master file creation / updating')
            """ START CREDIT PROCESS TO DETERMINE IF WE NEED TO ADD A CREDIT TO THEIR ACCOUNT """ 
            # (1) ONCE WE CREATE OR UPDATE THE MASTER FILE WE SUM UP THE TOTAL SPENT.
            DataFrame = pd.read_csv(master_file.file.url)
            total_sum_paid = DataFrame['Price'].sum()
            carrier_dvu = {}
            errors = []
            # FIND IF THE USER IS IN A CUSTOM RATE CARD TIER
            if user.rate_card_tier > 3: # if users tier is above 3 it must be a costume rate card in that case we want to use it
                tier_in_question = user.rate_card_tier
            else:
                tier_in_question = 3 # 3 is the enterprise rate card
       
                rate_card = RateCard.objects.filter(tier_rank=tier_in_question)
                if rate_card.exists():
                    tier_minimum_spend = rate_card.first().minimum_spend
                else:
                    # if there is no rate card for tier 3 send an email alert to dev to get one added and for the meantime set the minimum spend to 10 million dollars to avoid doing any calculations on a tier that does not exits
                    general_dev_alert_email('No rate card found for tier 3', 'No rate card found for tier 3 when sent form webhooks.py')
                    tier_minimum_spend = 10000000
            
            # (2) IF THE USER SPENT MORE THEN TIER X , CALCULATE WHAT THE PRICE WOULD BE IF THEY WERE IN TIER XX.
            if total_sum_paid >= tier_minimum_spend:
                users_pricing_queryset = RateCardItem.objects.filter(rate_card__tier_rank=tier_in_question, rate_card__expiration_date__gte=timezone.now())

                for carrier in users_pricing_queryset:
                    try:
                        carrier_dvu[carrier.carrier] = carrier.cost_per_DVU
                    except: 
                        errors.append['There is no rate card for the user']
                        
                # loop over the dataFrame and calculate the price for each row
                for index, row in DataFrame.iterrows():
                    # establish the carrier
                    carrier = DataFrame.loc[index]['ShippingMethodSelected']
                    dvu_for_carrier = carrier_dvu[carrier]
                    # how much the customer wants to insure the package for
                    declared_value = row['Value']
                    # add the price of how much we are going to charge to insure the package
                    cost = round((float(declared_value) / 100) * float(dvu_for_carrier), 2)
                    DataFrame.loc[index, 'Price'] = cost
                would_have_paid = DataFrame['Price'].sum() # with the newly calculated prices
                # (3) THEN SUBTRACT THE CURRENT PRICE FROM THE PRICE THEY WOULD HAVE PAID,
                initial_credit = round(total_sum_paid - would_have_paid, 2)
                # (4) THEN SEE IF THERE IS ANY CREDIT ON THERE ACCOUNT ALREADY FROM THIS MONTH AND DEDUCT THAT AMOUNT FROM THE CREDIT.
                credits = AddedCreditHistory.objects.filter(account_credit__user=user, created__month=timezone.now().month, created__year=timezone.now().year)
                previous_credit = credits.aggregate(Sum('amount_added'))
                # (5) IF THERE IS CREDIT, SUBTRACT THAT FROM THE DIFFERENCE.
                if previous_credit['amount_added__sum'] is None:
                    updated_credit = initial_credit
                else:
                    updated_credit = round(Decimal(credits) - previous_credit['amount_added__sum'], 2)
                updated_credit
                # (6) THE DIFFERENCE WILL BE ADDED TO THERE ACCOUNT AS CREDIT.
                if updated_credit > 0:
                    # find the users AccountCredit model
                    account_credit = AccountCredit.objects.get(user=user)
                    AddedCreditHistory.objects.create(account_credit=account_credit,
                                                    amount_added=updated_credit,
                                                    note=f'user qualified for a tier {tier_in_question} credit'
                                                    )
                    account_credit.credit_amount += updated_credit
                    account_credit.save()
                    # now create a new AddedCreditHistory model
                print('make it passed the credit process finished')
        except Exception as error:
            print(error)
            general_dev_alert_email('Error in webhook', error)
            print('Error in webhook')
