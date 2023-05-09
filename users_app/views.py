from utils.email_sender import send_contact_email, general_dev_alert_email
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .forms import ProfileForm, ContactForm
from pricing_app.models import ShipmentFile
from .services.selectors import get_orders
from django.views.generic import View
from django.contrib import messages
from django.views import debug
import pandas as pd
import sys


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.profile
        profile_form = ProfileForm(initial={'first_name': profile.first_name, 'last_name': profile.last_name, 'email': profile.email, 'address': profile.address, 'postal_code': profile.postal_code, 'city': profile.city})
        orders = get_orders(request)
        return render(request, 'profile/profile.html', {'orders': orders, 'profile_form': profile_form})

    def post(self, request):
        profile = request.user.profile 
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully', extra_tags='success')
            # return render(request, 'profile/profile.html', {'profile_form': profile_form})
            return redirect('profile')
        else:
            return render(request, 'profile/profile.html', {'profile_form': profile_form})
    
    
class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, file_id):
        file = get_object_or_404(ShipmentFile, id=file_id)
        
        DataFrame = pd.read_csv(file.file.url)
        # just in case error handling
        if DataFrame.empty:
            messages.error(request, 'File is empty', extra_tags='alert')
            return redirect('quote')
        else:
            
            total_price = DataFrame['Price'].sum()
            total_shipments = DataFrame.shape[0]
   
            context = {'DataFrame': DataFrame, 'total_price': total_price, 'file_id': file_id, 'file_path': file.file.url, 'in_cart': file.in_cart}        
            return render(request, 'profile/order_detail.html', context)
        
    def post(self, request):
            pass


class ShoppingCartView(LoginRequiredMixin, View):
    def get(self, request):
        # get all users files that are in the cart
        files = ShipmentFile.objects.filter(in_cart=True, user_id=request.user.id)
        return render(request, 'profile/shopping_cart.html', {'files': files})
        
    def post(self, request):
        file_id = request.POST.get('delete_file_id')
        file = get_object_or_404(ShipmentFile, id=str(file_id))
        file.in_cart = False
        file.save()
        return redirect('shopping_cart')
        
# htmx route
@login_required()
def add_to_cart(request, file_id):
    file = get_object_or_404(ShipmentFile, id=str(file_id))
    file.in_cart = True
    file.save()
    cart_count = ShipmentFile.objects.filter(in_cart=True, user_id=request.user.id).count()
    return render(request, 'fragments/shopping_cart_menu_link.html', {'cart_count': cart_count})
  





############### SITE VIEWS ####################

class ContactUsView(View):
    def get(self, request):
        contact_form = ContactForm()
        return render(request, 'site/contact.html', {'contact_form': contact_form})

    def post(self, request):
        contact_form = ContactForm(request.POST)
      
        if contact_form.is_valid():
            contact_form.save()
            email = contact_form.cleaned_data['email']
            name = contact_form.cleaned_data['name']
            message = contact_form.cleaned_data['message']
            send_contact_email(email, name, message)
            messages.success(request, 'Thank you for your message. We will get back to you soon.', extra_tags='success')
            return redirect('contact_us')
        return render(request, 'site/contact.html', {'contact_form': contact_form})



def email_terms_and_conditions(request):
    return render(request, 'site/email_terms_and_conditions.html')



########### error templates ############

def handler_404(request, exception):
    return render(request, 'base/404.html')

def handler_500(request):
    subject = f"{request.method} {request.path} [500]"
    message = debug.technical_500_response(request, *sys.exc_info()).content.decode('utf-8')
    general_dev_alert_email(subject, message)
    return render(request, 'base/500.html')