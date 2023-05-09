from django import forms
from django.core.exceptions import ValidationError
from .models import ShipmentFile, RateCard, RateCardItem
from django.contrib.auth import get_user_model




class FileUploadForm(forms.ModelForm):
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file.name.endswith('.csv'):
            if file.size > 5242880: # 5MB
                raise forms.ValidationError("File is larger then 5MB")
            return file
        else:
            raise forms.ValidationError("File Must be a CSV")
        
    class Meta:
        model = ShipmentFile
        fields = ['file']
        
    
    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': '.csv'})
        
        
class CreateRateCardForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all(), required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}), required=True)
    tier_rank = forms.ChoiceField(choices=RateCard.TIER_CHOICES, required=True)
    minimum_spend = forms.IntegerField(required=True)
    affective_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    

    def __init__(self, *args, **kwargs):
        can_edit_tier_rank = kwargs.pop('can_edit_tier_rank', None)
        super(CreateRateCardForm, self).__init__(*args, **kwargs)
        if not can_edit_tier_rank:
            self.fields['tier_rank'].widget.attrs.update({'disabled': 'disabled'})
            
    
    def clean(self):
        cleaned_data = super().clean()
        affective_date = cleaned_data.get('affective_date')
        expiration_date = cleaned_data.get('expiration_date')
        if affective_date and expiration_date:
            if affective_date > expiration_date:
                raise ValidationError("Expiration date must be after the affective date")
        return cleaned_data
    
    
class CreateRateCardItemForm(forms.Form):
    carrier = forms.ChoiceField(required=True)
    cost_per_DVU = forms.DecimalField()
    parcel_limit_price_cap = forms.ChoiceField(choices=RateCardItem.PARCEL_LIMIT)
    
    def __init__(self, *args, **kwargs):
        rate_card = kwargs.pop('rate_card', None)
        super(CreateRateCardItemForm, self).__init__(*args, **kwargs)
        # we only want the user selecting a carrier that is not already in the rate_card
        # we use a list comprehension to filter out the carriers that are already in the rate_card
        self.fields['carrier'].choices = [x for x in RateCardItem.CARRIER_CHOICES if x[0] not in rate_card.ratecarditem_set.values_list('carrier', flat=True)]
        