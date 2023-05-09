from django.db import models
import uuid
from django_countries.fields import CountryField
from users_app.models import CustomUser
from django.conf import settings
from utils.abstract_model import TimeStampedModel
from pricing_app.models import ShipmentFile


class Claim(TimeStampedModel):
    CLAIM_TYPES_CHOICES = (
        ('DAMAGE', 'Damage'),
        ('LOSS', 'Loss'),
        ('SHORTAGE', 'Shortage')
    )
    STATUS_CHOICES = (
        ('NEEDS MORE INFO', 'Needs_more_info'),
        ('PENDING INSURANCE RESPONSE', 'Pending_insurance_response'),
        ('SEND TO INSURANCE', 'Send_to_insurance'),
        ('CLOSED', 'Closed')
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    file = models.ForeignKey(ShipmentFile, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=False, blank=False)
    contact_name = models.CharField(max_length=100, null=False, blank=False)
    check_remit_country = CountryField(null=False, blank=False)
    check_remit_address = models.CharField(max_length=100, null=False, blank=False)
    check_remit_city = models.CharField(max_length=100, null=False, blank=False)
    check_remit_zip_code = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, null=False, blank=False)
    fax = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, null=False, blank=False)
    # about the package
    item_description = models.CharField(max_length=100, null=False, blank=False)
    invoice_or_package_id = models.CharField(max_length=100, null=False, blank=False)
    tracking_number = models.CharField(max_length=100, null=False, blank=False)
    ship_date = models.DateField(null=False, blank=False)
    type_of_claim = models.CharField(max_length=100, choices=CLAIM_TYPES_CHOICES, null=False, blank=False)
    is_item_repairable = models.BooleanField(blank=True, null=True, default=False)
    item_damage_or_shortage_description = models.CharField(max_length=100, blank=True, null=True)
    # package worth
    total_invoice_value = models.DecimalField(max_digits=10, decimal_places=0, null=False, blank=False)
    amount_recovered = models.DecimalField(max_digits=10, decimal_places=0, blank=False, null=False, default=0)
    insured_value = models.DecimalField(max_digits=10, decimal_places=0, null=False, blank=False, default=0)
    total_claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    # who was the package mailed to
    consignee_name = models.CharField(max_length=100, null=False, blank=False)
    consignee_email = models.EmailField()
    send_consignee_affidavit_request = models.BooleanField(default=False)
    consignee_country = CountryField(null=False, blank=False)
    # finishing up
    print_your_name = models.CharField(max_length=100, null=False, blank=False)
    sign_your_name = models.ImageField(upload_to='signatures', null=True, blank=True)
    status = models.CharField(max_length=35, choices=STATUS_CHOICES, default='SEND TO INSURANCE')
    notes = models.TextField(blank=True, null=True)
    
