from django import forms
# from django.contrib.auth import get_user_model
from .models import ShippingQuote

class ShippingQuoteForm(forms.ModelForm):
    class Meta:
        model = ShippingQuote
        fields = ['email', 'first_name', 'last_name', 'phone', 
                  'company_name','state','city','zip_code','parcel_weight',
                  'parcel_shipped_per_month', 'shipping_software',
                  'how_did_you_hear_about_us', 'preferred_contact_time', 'comments']
        
        widgets = {
            'phone': forms.TextInput(attrs={'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'}),
            'preferred_contact_time': forms.TextInput(attrs={'type': 'datetime-local'}),
        }

    # this method is should be used when needing a dynamic form that the initial values or widgets need to change based on
    # user input or changes in the database or some other data in general the 2 methods are good and setting the widgets in the meta class
    # is good for static forms and can be a source of documentation for the informed developer of the forms functionality
    
    # def __init__(self, *args, **kwargs):
    #     super(ShippingQuoteForm, self).__init__(*args, **kwargs)
    #     self.fields['phone'].widget.attrs.update({'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'})
    def __init__(self, *args, **kwargs):
        super(ShippingQuoteForm, self).__init__(*args, **kwargs)
        self.fields['parcel_weight'].initial = ShippingQuote.PARCEL_WEIGHT_CHOICES[0][0]
        self.fields['parcel_shipped_per_month'].initial = ShippingQuote.PARCEL_SHIPPED_CHOICES[0][0]
        self.fields['shipping_software'].initial = ShippingQuote.SOFTWARE_CHOICES[0][0]
        self.fields['state'].initial = "NY"
        # self.fields['preferred_contact_time'].initial = 
        