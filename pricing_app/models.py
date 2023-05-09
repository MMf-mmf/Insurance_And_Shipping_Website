from django.core.validators import FileExtensionValidator
from utils.abstract_model import TimeStampedModel
from django.conf import settings
from django.db import models
import uuid

# model for storing shipments file. we treat this as a product model.
class ShipmentFile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='shipments_files/%Y/%m/%d', null=False, blank=False,
                            validators=[
                                FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls'])
                            ])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipments_file', null=True, default=None)
    # if there is no user, store the ip address as a identifier
    ip_address = models.GenericIPAddressField(null=True, default=None)
    total_shipments = models.CharField(null=False, blank=True, max_length=255, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True,blank=True, default=None)
    description = models.TextField(null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    in_cart = models.BooleanField(default=False)
    

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.file.name
 
# models for Rate Cards
class RateCard(TimeStampedModel):
    TIER_CHOICES = (
        (1, 'Guest'),
        (2, 'Company'),
        (3, 'Enterprise'),
        (4, 'Custom') 
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tier_rank = models.PositiveIntegerField(null=False, blank=False, choices=TIER_CHOICES, default=1)
    minimum_spend = models.PositiveIntegerField(null=False, blank=False)
    affective_date = models.DateField(null=False, blank=False)
    expiration_date = models.DateField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rate_card', null=True, default=None)
    

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.description
    
    
# every shipment service gets its own RateCardItem (such as ups ground etc will get its own rateCardItem)
class RateCardItem(TimeStampedModel):
    CARRIER_CHOICES = (
        ('DHL eCommerce', 'DHL eCommerce'),
        ('DHL eCommerce International', 'DHL eCommerce International'),
        ('DHL Express Domestic', 'DHL Express Domestic'),
        ('DHL Express International', 'DHL Express International'),
        ('FedEx Domestic', 'FedEx Domestic'),
        ('FedEx International', 'FedEx International'),
        ('LaserShip Domestic', 'LaserShip Domestic'),
        ('UPS Domestic', 'UPS Domestic'),
        ('UPS International', 'UPS International'),
        ('UPS Domestic B to B', 'UPS Domestic B to B'),
        ('USPS Domestic', 'USPS Domestic'),
        ('USPS International', 'USPS International'),
    )
    
    PARCEL_LIMIT = (
        ('10000', '10000'),
        ('25000', '25000'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rate_card = models.ForeignKey(RateCard, on_delete=models.CASCADE, null=False, blank=False)
    carrier = models.CharField(max_length=255, choices=CARRIER_CHOICES, null=False, blank=False)
    cost_per_DVU = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    parcel_limit_price_cap = models.DecimalField(max_digits=5, decimal_places=0,choices=PARCEL_LIMIT, null=False, blank=False)
    
    
    # add constraint to assure that there can only be unique carrier per rate_card
    # class Meta:
    #     unique_together = ('rate_card', 'carrier')
    
    def __str__(self):
        return self.carrier + ' - ' + str(self.cost_per_DVU)
    


