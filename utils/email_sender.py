from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

# utils function
# this is a reusable function that can be used to send emails by other functions just pass the first 3 mandatory arguments
def send_email(email_to, subject, email_template_path, context=None, file=None):
    if not isinstance(email_to, list):
        email_to = [email_to]
    html_content = render_to_string(email_template_path, context)
    email = EmailMessage(subject,
                        html_content,
                        settings.DEFAULT_FROM_EMAIL,
                        email_to,
            )
    if file != None:
        email.attach(file.file.name, file.file.read())
    email.content_subtype = "html" 
    email.send(fail_silently=False)
    
    
    
def send_refund_email(order):
    email_to = order.email
    subject = f'Allin1ship - Refund for order #{order.id}'
    email_template_path = 'email/order_refund.html'
    send_email(email_to, subject, email_template_path, context={'order': order})
    

def send_contact_email(email, name, message):
    email_to = settings.DEFAULT_FROM_EMAIL
    subject = f'Allin1ship - Contact form'
    email_template_path = 'email/contact_form.html'
    send_email(email_to, subject, email_template_path, context={'email': email, 'name': name, 'message': message})
    
def send_shipping_quote_email(quote_form):
    email_to = settings.DEFAULT_COSTUMER_SERVICE_EMAIL
    subject = f'Allin1ship - Shipping Quote'
    email_template_path = 'shipping_app/email/get_shipping_quote.html'
    # unpack the form data
    email = quote_form.cleaned_data['email']
    first_name = quote_form.cleaned_data['first_name']
    last_name = quote_form.cleaned_data['last_name']
    phone = quote_form.cleaned_data['phone']
    state = quote_form.cleaned_data['state']
    city = quote_form.cleaned_data['city']
    zip_code = quote_form.cleaned_data['zip_code']
    company_name = quote_form.cleaned_data['company_name']
    parcel_shipped_per_month = quote_form.cleaned_data['parcel_shipped_per_month']
    shipping_software = quote_form.cleaned_data['shipping_software']
    preferred_contact_time = quote_form.cleaned_data['preferred_contact_time']
    how_did_you_hear_about_us = quote_form.cleaned_data['how_did_you_hear_about_us']
    comments = quote_form.cleaned_data['comments']
    
    # send email by calling the send_email function with all the appropriate arguments
    send_email(email_to, subject, email_template_path, context={ 'email': email,
                                                                'first_name': first_name,
                                                                'last_name': last_name,
                                                                'phone': phone,
                                                                'company_name': company_name,
                                                                'state': state,
                                                                'city': city,
                                                                'zip_code': zip_code,
                                                                'parcel_shipped_per_month': parcel_shipped_per_month,
                                                                'shipping_software': shipping_software,
                                                                'preferred_contact_time': preferred_contact_time,
                                                                'how_did_you_hear_about_us': how_did_you_hear_about_us,
                                                                'comments': comments}
               )
    
def send_order_confirmation_email(order, file):
    email_to = order.email
    subject = f'Allin1ship - Order #{order.id}'
    email_template_path = 'email/order_success.html'
    context = {'order#': order.id}
    send_email(email_to, subject, email_template_path, context=context, file=file)
    
    
    
def dev_alert_email(model, *args, **kwargs):
    email_to = settings.DEFAULT_DEV_EMAIL_2
    subject = f'Allin1ship - {model} does not exist'
    email_template_path = 'email/dev_alert.html'
    send_email(email_to, subject, email_template_path, context={'model': model, 'args': args, 'kwargs': kwargs})
    
def general_dev_alert_email(title ,message):
    email_to = [settings.DEFAULT_DEV_EMAIL_2, settings.DEFAULT_DEV_EMAIL]
    subject = f'Allin1ship - {title}'
    email_template_path = 'email/general_dev_alert.html'
    send_email(email_to, subject, email_template_path, context={'title': title,'message': message})
    
def send_claim_field_email(tracking_number, claim_amount, claim_id, base_url):
    email_to = settings.DEFAULT_COSTUMER_SERVICE_EMAIL
    subject = f'Allin1ship - Claim filed for {tracking_number}'
    email_template_path = 'email/claim_filed_to_admin.html'
    send_email(email_to, subject, email_template_path, context={'tracking_number': tracking_number, 'claim_amount': claim_amount, 'claim_id': claim_id, 'base_url': base_url})
    
def  send_claim_email_to_client(tracking_number, total_claim_amount, claim_id, BASE_URL, users_email):
    email_to = users_email
    subject = f'Allin1ship - We received your claim for tracking number {tracking_number}'
    email_template_path = 'email/claim_filed_to_client.html'
    send_email(email_to, subject, email_template_path, context={'tracking_number': tracking_number, 'total_claim_amount': total_claim_amount, 'claim_id': claim_id, 'BASE_URL': BASE_URL})