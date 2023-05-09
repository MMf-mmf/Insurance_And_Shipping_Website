import base64
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django import forms
from .models import Claim



class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ('company_name',
                'contact_name',
                'check_remit_address',
                'check_remit_city',
                'check_remit_country',
                'check_remit_zip_code',
                'phone',
                'fax',
                'email',
                'item_description',
                'invoice_or_package_id',
                'tracking_number',
                'ship_date',
                'type_of_claim',
                'is_item_repairable',
                'item_damage_or_shortage_description',
                'total_invoice_value', 'insured_value',
                'amount_recovered',
                'total_claim_amount', 
                'consignee_name',
                'consignee_email',
                'consignee_country',
                'print_your_name',
                'send_consignee_affidavit_request',
                )
        
        widgets = {
            'phone': forms.TextInput(attrs={'type': 'tel', 'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'}),
            'ship_date': forms.TextInput(attrs={'type': 'date'}),
            # 'total_claim_amount': forms.TextInput(attrs={'readonly': 'readonly'}),
            # 'insured_value': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
   
 

class AdminUpdateClaimForm(forms.Form):
    # create from for notes and status
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}), required=False)
    status = forms.ChoiceField(choices=Claim.STATUS_CHOICES)


         
     
        