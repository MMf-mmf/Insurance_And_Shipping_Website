from django import forms
from .models import Order, OrderItem

# form for Order model
class OrderForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'discount_applied')
        
    def __init__(self, *args, **kwargs):
        credit = kwargs.pop('credit', None)
        total_price = kwargs.pop('order_total', None)
        # get the smaller value between credit and total_price
        super(OrderForm, self).__init__(*args, **kwargs)
        if credit == None or credit < 1:
            self.fields.pop('discount_applied')
        else:
            max_input = min(credit, total_price)
            self.fields['discount_applied'].widget.attrs['max'] = max_input  
            

