import pandas as pd
from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from .forms import FileUploadForm, CreateRateCardForm, CreateRateCardItemForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import ShipmentFile, RateCard, RateCardItem
from django.contrib import messages
from .services.uploaded_file_service import file_felid_validations, handle_file_upload
from utils.helper_functions import download_csv, download_csv_from_cloud
from django.contrib.auth.decorators import login_required
import random

class AdminOrStaff(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    
class Quote(View):
    def get(self, request):
        form = FileUploadForm()
        return render(request, "quote.html", {'form': form})

    def post(self, request):
        return render(request, "quote.html")

######## DOWNLOAD TEMPLATE FILE'S ########
def download_template_file(request):
    file_path = 'static/files/shipmentsTemplate.csv'
    return download_csv(file_path)

def download_sample_file(request):
    file_path = 'static/files/shipmentsSample.csv'
    return download_csv(file_path)

def download_shipments_file_with_pricing(request, file_id):
    file = get_object_or_404(ShipmentFile, id=file_id)
    return download_csv_from_cloud(file)


########### UPLOAD FILE OF SHIPMENTS TO GET A QUOTE ############
def upload_file(request):
    form = FileUploadForm(request.POST, request.FILES)
   
    if form.is_valid():
        file = form.cleaned_data['file']
        # update the file name to the file name plus a random string value before the file extension
        file.name = file.name.split('.')[0] + str(random.randint(1000, 9999)) + '.' + file.name.split('.')[1]
        file_or_error = file_felid_validations(request,file)
        # if the file is valid, then handle the file upload
        if isinstance(file_or_error ,list) == False: # if the file has no errors
            # call function from service to handle handle the actual file upload
            shipment = handle_file_upload(request, file)
            if not shipment:
                messages.error(request, 'Error Uploading file. Please contact customer support', extra_tags='alert')
                return redirect('pricing_app:quote')
            return redirect('pricing_app:upload_breakdown', str(shipment.id))
        
        # file has errors
        messages.error(request, file_or_error[0], extra_tags='alert')
        return redirect('pricing_app:home')
    
    
    # form not valid, message

    messages.error(request, form.errors['file'], extra_tags='alert')
    return redirect('pricing_app:home')

class UploadBreakdown(View):
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

            try:
                file.price = total_price
                file.total_shipments = total_shipments
                file.save()
                
            except KeyError:
                messages.error(request, 'Please contact customer service ( error parsing Price colum )', extra_tags='alert')
                return redirect('quote')
            
            context = {'DataFrame': DataFrame, 'total_price': total_price, 'file_id': file_id, 'file_path': file.file, 'in_cart': file.in_cart}        
            return render(request, "shipments_breakdown.html", context)

    def post(self, request):
        return render(request, "shipments_breakdown.html")



class CreateRateCardView(View):
    def get(self, request):
        create_rate_card_form = CreateRateCardForm(can_edit_tier_rank=True)
        return render(request, "create_rate_card.html", {'create_rate_card_form': create_rate_card_form})

    def post(self, request):
        create_rate_card_form = CreateRateCardForm(request.POST, can_edit_tier_rank=True)
        if create_rate_card_form.is_valid():
            user = create_rate_card_form.cleaned_data['user']
            tier_rank = create_rate_card_form.cleaned_data['tier_rank']
            minimum_spend = create_rate_card_form.cleaned_data['minimum_spend']
            description = create_rate_card_form.cleaned_data['description']
            affective_date = create_rate_card_form.cleaned_data['affective_date']
            expiration_date = create_rate_card_form.cleaned_data['expiration_date']
            if user:
                rate_card = RateCard.objects.create(
                                description=description,
                                affective_date=affective_date,
                                expiration_date=expiration_date,
                                tier_rank=tier_rank,
                                minimum_spend=minimum_spend,
                                user=user,
                            )
            else:
                rate_card = RateCard.objects.create(
                                description=description,
                                affective_date=affective_date,
                                expiration_date=expiration_date,
                                tier_rank=tier_rank,
                                minimum_spend=minimum_spend,
                            )
                
            messages.success(request, 'Rate Card Created', extra_tags='alert')
            return redirect('pricing_app:rate_cards')
        messages.error(request, 'Error Creating Rate Card', extra_tags='alert')
        return render(request, "create_rate_card.html", {'create_rate_card_form': create_rate_card_form})
    
    

class RateCardDetailView(View):
    def get(self, request, rate_card_id):
        rate_card = get_object_or_404(RateCard, id=rate_card_id)
        rate_card_items = RateCardItem.objects.filter(rate_card=rate_card)
        create_rate_card_form = CreateRateCardForm(can_edit_tier_rank=False,
                                                   initial={
                                                       'description': rate_card.description,
                                                       'affective_date': rate_card.affective_date,
                                                       'expiration_date': rate_card.expiration_date,
                                                       'tier_rank': rate_card.tier_rank,
                                                       'minimum_spend': rate_card.minimum_spend,
                                                       'user': rate_card.user
                                                       }
                                                   )
        create_rate_card_item_form = CreateRateCardItemForm(rate_card=rate_card)
        return render(request, "rate_card_detail.html", {'rate_card': rate_card, 'create_rate_card_form': create_rate_card_form, 'create_rate_card_item_form': create_rate_card_item_form, 'rate_card_items': rate_card_items})

    def post(self, request, rate_card_id):
      
        if 'submit' in request.POST:
            # HANDLE POST REQUEST FROM THE UPDATE RATE CARD FORM
            create_rate_card_form = CreateRateCardForm(request.POST, can_edit_tier_rank=False)
            rate_card = get_object_or_404(RateCard, id=rate_card_id)
            if create_rate_card_form.is_valid():
                rate_card.description = create_rate_card_form.cleaned_data['description']
                rate_card.affective_date = create_rate_card_form.cleaned_data['affective_date']
                rate_card.expiration_date = create_rate_card_form.cleaned_data['expiration_date']
                rate_card.tier_rank = create_rate_card_form.cleaned_data['tier_rank']
                rate_card.minimum_spend = create_rate_card_form.cleaned_data['minimum_spend']
                if create_rate_card_form.cleaned_data['user']:
                    rate_card.user = create_rate_card_form.cleaned_data['user']
                rate_card.save()
                messages.success(request, 'Rate Card Updated', extra_tags='alert')
                return redirect('pricing_app:rate_cards')
            messages.error(request, 'Error Updating Rate Card', extra_tags='alert')
            return render(request, "rate_card_detail.html", {'rate_card': rate_card, 'create_rate_card_form': create_rate_card_form})
        elif 'delete' in request.POST:
            rate_card = get_object_or_404(RateCard, id=rate_card_id)
            rate_card.delete()
            messages.success(request, 'Rate Card Deleted', extra_tags='alert')
            return redirect('pricing_app:rate_cards')
    

class CreateRateCardItemView(AdminOrStaff):
    def post(self, request, rate_card_id):
        rate_card = get_object_or_404(RateCard, id=rate_card_id)
        create_rate_card_item_form = CreateRateCardItemForm(request.POST, rate_card=rate_card)
        if create_rate_card_item_form.is_valid():
            rate_card_item = RateCardItem.objects.create(
                                rate_card=rate_card,
                                carrier = create_rate_card_item_form.cleaned_data['carrier'],
                                cost_per_DVU = create_rate_card_item_form.cleaned_data['cost_per_DVU'],
                                parcel_limit_price_cap = create_rate_card_item_form.cleaned_data['parcel_limit_price_cap'],
                            )
            messages.success(request, 'Rate Card Item Created', extra_tags='alert')
            return redirect('pricing_app:rate_card_detail', rate_card_id=rate_card.id)
        messages.error(request, 'Error Creating Rate Card Item', extra_tags='alert')
        return render(request, "rate_card_detail.html", {'rate_card': rate_card, 'create_rate_card_form': create_rate_card_form, 'create_rate_card_item_form': create_rate_card_item_form})


class DeleteRateCardItemView(AdminOrStaff):
    def post(self, request, rate_card_id, rate_card_item_id):
        rate_card = get_object_or_404(RateCard, id=rate_card_id)
        rate_card_item = get_object_or_404(RateCardItem, id=rate_card_item_id)
        rate_card_item.delete()
        messages.success(request, 'Rate Card Item Deleted', extra_tags='alert')
        return redirect('pricing_app:rate_card_detail', rate_card_id=rate_card.id)


# MENU BAR LINKS

class RateCardListView(AdminOrStaff):
    def get(self, request):
        rate_cards = RateCard.objects.all()
        context = {'rate_cards': rate_cards}
        return render(request, "rate_card_list.html", context)

    def post(self, request):
        rate_cards = RateCard.objects.all()
        context = {'rate_cards': rate_cards}
        return render(request, "rate_card_list.html", context)
    
    
def home(request):
    form = FileUploadForm()
    rate_card = RateCard.objects.filter(tier_rank=3)
    if rate_card.exists():
        minimum_spend = rate_card.first().minimum_spend
    else:
        minimum_spend = '10,000'

    return render(request, 'site/home.html', {'file_upload_form': form, 'minimum_spend': minimum_spend})

def pricing(request):
    rate_card = RateCard.objects.filter(tier_rank=3)
    if rate_card.exists():
        minimum_spend = rate_card.first().minimum_spend
    else:
        minimum_spend = '10,000'
    return render(request, 'site/pricing.html', {'minimum_spend': minimum_spend})

def about(request):
    return render(request, 'site/about.html')



