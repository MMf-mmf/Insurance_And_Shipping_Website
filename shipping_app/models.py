from django.db import models
import uuid



class ShippingQuote(models.Model):
    PARCEL_WEIGHT_CHOICES = (
        ('1-4 Oz', '1-4 Oz'),
        ('5-11 Oz', '5-11 Oz'),
        ('12-16 Oz', '12-16 Oz'),
        ('1-3 Lbs', '1-3 Lbs'),
        ('4-6 Lbs', '4-6 Lbs'),
        ('6-25 Lbs', '6-25 Lbs'),
        ('26+ Lbs', '26+ Lbs'),
    )

    PARCEL_SHIPPED_CHOICES = (
        ('1-1000', '1-1000'),
        ('1000-3000', '1000-3000'),
        ('3000-5000', '3000-5000'),
        ('5000+', '5000+'),
    )

    SOFTWARE_CHOICES = (
        ('ShipStation', 'ShipStation'),
        ('Stamps.com', 'Stamps.com'),
        ('ShipWorks', 'ShipWorks'),
        ('SellerCloud (shipBridge)', 'SellerCloud'),
        ('ShippingEasy', 'ShippingEasy'),
        ('ShipRush', 'ShipRush'),
        ('Endicia', 'Endicia'),
        ('Shippo', 'Shippo'),
        ('ShipSaver', 'ShipSaver'),
        ('eBay Labels', 'eBay Labels'),
        ('PayPal Multi-Order Shipping', 'PayPal Multi-Order Shipping'),
        ('Other', 'Other'),
    ) 

    HEAR_ABOUT_US_CHOICES = (
        ('Referral', 'Referral'),
        ('Search Engine', 'Search Engine'),
        ('Advertisement', 'Advertisement'),
        ('Social Media', 'Social Media'),
        ('Other', 'Other')
    )
    US_STATES_CHOICES = (
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('DC', 'District Of Columbia'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=50, null=False, blank=False)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    phone = models.CharField(max_length=50, null=False, blank=False)
    
    company_name = models.CharField(max_length=50, null=False, blank=False)
    state = models.CharField(max_length=2, null=False, blank=False, choices=US_STATES_CHOICES)
    city = models.CharField(max_length=15, null=False, blank=False)
    zip_code = models.CharField(max_length=6, null=False, blank=False)
    
    parcel_weight = models.CharField(max_length=10, choices=PARCEL_WEIGHT_CHOICES, null=False, blank=False)
    parcel_shipped_per_month = models.CharField(max_length=10, choices=PARCEL_SHIPPED_CHOICES, null=False, blank=False)
    shipping_software = models.CharField(choices=SOFTWARE_CHOICES ,max_length=50, null=False, blank=False)
    
    preferred_contact_time = models.DateTimeField(null=True, blank=True)
    how_did_you_hear_about_us = models.CharField(choices=HEAR_ABOUT_US_CHOICES ,max_length=50, null=True, blank=True)
    comments = models.TextField(max_length=300, null=False, blank=True)
    
    def __str__(self):
        return self.email + ' ' + self.company_name