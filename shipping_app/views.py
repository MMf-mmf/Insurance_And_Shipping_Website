from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import ShippingQuoteForm
from django.contrib import messages
from utils.email_sender import send_shipping_quote_email


class ShippingQuoteView(View):
    def get(self, request):
        quote_form = ShippingQuoteForm()
        return render(request, 'shipping_app/shipping_quote.html', {'quote_form': quote_form})
    
    def post(self, request):
        quote_form = ShippingQuoteForm(request.POST)
        if quote_form.is_valid():
            quote_form.save()
            send_shipping_quote_email(quote_form)
            messages.success(request, 'Thank you for your interest in our services. Please allow up to 2 Business for a response.', extra_tags='success')
            return redirect('shipping_quote')
        # check if the form data is valid then if the data is from the choice 
        # field of the the text field taking input from the user that selects other
        
        return render(request, 'shipping_app/shipping_quote.html', {'quote_form': quote_form})

