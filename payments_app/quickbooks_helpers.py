from django.conf import settings
from django.shortcuts import redirect
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
# from .models import QuickbooksTokens
from django.db import transaction
import requests, json, textwrap, base64
# from payments_app.models import Order, OrderItem, QuickbooksTokens
import pandas as pd
from django.utils import timezone
from datetime import timedelta
################################## AUTHENTICATION #########################################
# https://oauth-pythonclient.readthedocs.io/en/latest/index.html
# https://github.com/IntuitDeveloper/SampleOAuth2_UsingPythonClient/blob/master/app/views.py

# AS OF NOW THESE FUNCTIONS WILL NOT BE USED TO MAINTAIN PREVENT STORING THE REFRESH TOKEN IN THE DATABASE
# when we do not have a valid refresh token we can get one with this function
def initialize_qb_authentication(request):
    # initialize the auth client
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )
    # get authorization url this is done by specifying the scopes you want to access
    url = auth_client.get_authorization_url([Scopes.ACCOUNTING, Scopes.PAYMENT, Scopes.EMAIL, Scopes.PROFILE, Scopes.PHONE, Scopes.ADDRESS])
    request.session['state'] = auth_client.state_token
    return redirect(url)

def get_tokens(request,auth_code, realm_id):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        state_token=request.session.get('state', None),
    )
    auth_client.get_bearer_token(auth_code=auth_code, realm_id=realm_id)
    qs = QuickbooksTokens.objects.all()
    if len(qs) > 0:
        try:
            qs = QuickbooksTokens.objects.get(id=1)
            qs.access_token = auth_client.access_token
            qs.access_expires_in = auth_client.expires_in
            qs.refresh_expires_in = auth_client.x_refresh_token_expires_in
            qs.save()
        except QuickbooksTokens.DoesNotExist:
            print('it seems the the original object has been deleted and new the database first object douse not have the value 1 anymore')
    else:
        QuickbooksTokens.objects.create(
            access_token=auth_client.access_token,
            )
    return auth_client.access_token
    
    
    
    
def refresh_tokens():
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )
    # as of now we are going to get the token from the environment variables which will be set every 100 days
    auth_client.refresh(refresh_token=settings.QB_REFRESH_TOKEN)
    # store access token in database
    qs = QuickbooksTokens.objects.all()
    if len(qs) == 0:
        QuickbooksTokens.objects.create(
            access_token=auth_client.access_token,
        )
    else:
        qs = QuickbooksTokens.objects.get(id=1)
        qs.access_token = auth_client.access_token
        qs.save()
        
        
        
        
        
###################### CREATE INVOICE ############################
def create_invoice(request, order, shipment_file):
    errors = []
    # if the order has a payment link already return the link
    if order.quickbooks_payment_link:
        return order.quickbooks_payment_link
    if order.paid == True:
        errors.append('This order has already been payed for')
        return errors
    # if the order has already been payed for return a message in the errors that the order has already been payed for
    
    # establish the access token
    # if the is models modified attribute is more than 60 minutes old refresh the token
    if QuickbooksTokens.objects.first().modified < (timezone.now() - timedelta(minutes=60)):
        refresh_tokens()
    access_token = QuickbooksTokens.objects.first().access_token
    # establish the order_items
    items = order.items.all()
    
    
    """QUICKBOOKS REQUEST HEADERS"""
    create_invoice = f'https://sandbox-quickbooks.api.intuit.com/v3/company/{settings.REALM_ID}/invoice?minorversion=65'
    # HEADER FOR UPLOADING ATTACHMENT
    upload_attachment_url = f'https://sandbox-quickbooks.api.intuit.com/v3/company/{settings.REALM_ID}/upload'

    create_request_invoice_headers = {'Accept': 'application/json', 'Authorization': f'Bearer {access_token}'}

    attachment_url_headers = {'Accept': 'application/json',
                                    'Content-Type': 'text/plain',
                                    'User-Agent': 'python-quickbooks api link',
                                    'Content-Type': 'multipart/form-data;boundary=37a1965f87babd849241a530ad71e169',
                                    'Authorization': f'Bearer {access_token}',
                                    'Accept-Encoding': 'gzip;q=1.0,deflate;q=0.6,identity;q=0.3',
                                    'Connection': 'close',
                                    }
    
    """QUICKBOOKS REQUEST BODY"""
    def create_invoice_body(email='tes@t.com'):
        invoice_body = {
            "Line": [],
            "CustomerRef": {
                "value": "1"
            },
            "BillEmail": {
                "Address": email
            },
        }
        return invoice_body
    
    
    invoice_body = create_invoice_body()
    
    for i, item in enumerate(items):
        invoice_body["Line"].append(
           {
                "Id": i + 1 ,
                "LineNum": i + 1,
                "Description": f'{item.shipping_service}',
                "Amount": str(item.price),
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {
                        "value": "2",
                        "name": "Services"
                    },
                "Qty": int(item.quantity),
                    "ItemAccountRef": {
                        "value": "1",
                        "name": "Services"
                    },
                }
            }
        )
        

    response = requests.post(
        create_invoice,
        json=invoice_body,
        headers=create_request_invoice_headers
    )
    
    if response:
        # GET THE INVOICE ID FROM THE NEWLY CREATED ID
        jsonRespons = json.loads(response.text)
        new_invoice_id = jsonRespons['Invoice']['Id']
        invoice_number = jsonRespons['Invoice']['DocNumber']
        payment_link = jsonRespons['Invoice']['InvoiceLink']
        
        ########### UPLOAD THE ATTACHMENT  ############
        file_path = order.shipment_file.file.path
        base_df = pd.read_csv(file_path)
        csv_file = base_df.to_csv()

        binary_file_data = str(base64.b64encode(bytes(csv_file, 'utf-8')).decode('ascii'))
        # this line just ads a line break every 50 characters
       
        
        file_name ='insurance_breakdown.csv'
        attachment_body = get_attachment_file_body(new_invoice_id, file_name, binary_file_data)
        
        res = requests.post(
            upload_attachment_url,
            headers=attachment_url_headers,
            data=attachment_body,
        )
        if res:
            print(res.text)
            order.quickbooks_payment_link = payment_link
            order.save()
        # the attachment failed to upload
        else:
            errors.append('A Error has occurred when attaching file to invoice.')
            print(res.content)
           
        
    # the invoice failed to create
    else:
        errors.append('A Error has occurred when trying to create the invoice.')
        print(response.content)
        
        
        
    """END OF FUNCTION RETURN ERRORS OR INVOICE NUMBER"""
    if len(errors) > 0:
        return errors
    else:
        return payment_link

        
    # GET THE COMPLEX multipart/form-data TO PLACE IN THE REQUEST BODY
    # EVERY INDENTATION AS WELL AS LINE BREAKS ARE IMPORTANT
def get_attachment_file_body(new_invoice_id, file_name, binary_file_data):
    attachment_request_body = textwrap.dedent("""
    {
        "AttachableRef": [
        {
          "EntityRef": {
            "type": "Invoice",
            "value": "%s"
          },
          "IncludeOnSend": true
        }
      ],
      "FileName": "%s",
        "ContentType": "text/csv"
      }
      
    """) % (new_invoice_id, file_name)

    attachment_request_body = textwrap.dedent(
        """
    --37a1965f87babd849241a530ad71e169
    Content-Disposition: form-data; name="file_metadata_0"
    Content-Type: application/json
    %s
    --37a1965f87babd849241a530ad71e169
    Content-Disposition: form-data; name="file_content_0"; filename="%s"
    Content-Type: text/csv
    Content-Transfer-Encoding: base64
    
    %s
    
    --37a1965f87babd849241a530ad71e169--      
    """
    ) % (attachment_request_body, file_name, binary_file_data)

    return str(attachment_request_body)
    
    
    
    
    
    
    
