from utils.abstract_model import TimeStampedModel
from pricing_app.models import ShipmentFile
from users_app.models import CustomUser
from django.conf import settings
from django.db import models
import uuid

class Order(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   
    user = models.ForeignKey(CustomUser, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    
    shipment_file = models.ForeignKey(ShipmentFile, related_name='order', on_delete=models.DO_NOTHING, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    address = models.CharField(max_length=250, null=False, blank=False)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=False, blank=False)
    
    total_shipments = models.PositiveIntegerField(default=1) # total number of shipment on the uploaded file
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True) # total cost of the order
    discount_applied = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True) # date the order was paid 
    stripe_payment_intent = models.CharField(max_length=50, null=True, blank=True)
    stripe_id = models.CharField(max_length=50, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True) # date the order was refunded
    # not in use remove if quckbooks is still not used a while after the app is in use
    quickbooks_id = models.CharField(max_length=50, null=True, blank=True)
    quickbooks_payment_link = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_stripe_url(self):
        if not self.stripe_id:
            return None
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path= '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'
    
    
    # order the orders by last created
    class Meta:
        ordering = ['-modified']
    
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # create item for each shipment service in the file the user is trying to insure
    shipping_service = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
# INSURED SHIPMENTS PER MONTH PER USER ( EVERY USER WILL HAVE ONE FILE OF ALL SHIPMENTS THEY INSURED)
class InsuredShipments(TimeStampedModel):
    # inherits created and modified from TimeStampedModel
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='insured_shipments/%Y/%m', null=True, blank=True)
    user = models.ForeignKey(CustomUser, related_name='insured_shipments', on_delete=models.CASCADE, null=False, blank=False)
    
    def __str__(self):
        return f'{self.user} + "owens" + {self.file}'
    
    class Meta:
        ordering = ['-modified']
    
#  NOT IN USE REMOVE IF QUICKBOOKS IS NOT USED A WHILE AFTER THE APP IS IN USE
# class QuickbooksTokens(TimeStampedModel):
#     access_token = models.CharField(max_length=863, null=False, blank=False)
#     refresh_token = models.CharField(max_length=255, null=True, blank=True)
#     realm_id = models.CharField(max_length=255, null=True, blank=True)
#     # access_token_expires_at = models.DateTimeField(null=True, blank=True)
#     # refresh_token_expires_at = models.DateTimeField(null=True, blank=True)
#     def __str__(self):
#         return f'{self.id}'
    
    

class AccountCredit(TimeStampedModel):
    # inherits created and modified from TimeStampedModel
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, related_name='credits', on_delete=models.CASCADE, null=False, blank=False)
    admin = models.ForeignKey(CustomUser, related_name='admin_credits', on_delete=models.CASCADE, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False, default=0.00)
    is_valid = models.BooleanField(default=True)
    

class SpentCreditHistory(TimeStampedModel):
    # the created field will be used for the spent date
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_credit = models.ForeignKey(AccountCredit, related_name='history', on_delete=models.CASCADE, null=False, blank=False)
    amount_used = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    note = models.CharField(max_length=255, null=True, blank=True)
    
    
class AddedCreditHistory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_credit = models.ForeignKey(AccountCredit, related_name='added_history', on_delete=models.CASCADE, null=False, blank=False)
    amount_added = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    note = models.CharField(max_length=255, null=True, blank=True)
    
    