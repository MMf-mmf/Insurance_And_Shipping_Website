from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ClaimForm, AdminUpdateClaimForm
from django.contrib import messages
import base64
from django.core.files.base import ContentFile
from users_app.models import CustomUser
from pricing_app.models import ShipmentFile
from utils.helper_functions import get_object_or_email_alert
from utils.email_sender import send_claim_field_email, send_claim_email_to_client
from django.shortcuts import get_object_or_404
from .models import Claim
from django.conf import settings

class AdminOrStaff(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    

class StartClaimView(LoginRequiredMixin,View):
    def get(self, request):
        claim_form = ClaimForm()
        
        return render(request, 'claims_app/start_claim.html', {'claim_form': claim_form})
    
    def post(self, request):
        claim_form = ClaimForm(request.POST)
        sign_your_name = request.POST.get('sign_your_name')
        file_id = request.GET.get('file')
        # if the user is coming from the order detail page there should be a file_id in the query params to link the claim to which in turn can also be linked to the order 
        if file_id:
            file = get_object_or_email_alert(ShipmentFile, id=file_id)
        else:
            file = None
        # if the sign_your_name is empty add a error message to the form that the form must be signed
        if sign_your_name == '':
            claim_form.add_error(None, 'Please sign the form before submitting.')
            
        if claim_form.is_valid():
            claim = claim_form.save()
            # once the data in the form has been saved lets add the user and image to the claim
            claim.user = request.user
            if file:
                claim.file = file
            format, base64_string = sign_your_name.split(';base64,') # separate the meta data from the base64 string
            signature_data = base64.b64decode(base64_string)         # decode the base64 string so it can be saved as a file
            claim.sign_your_name.save('sigImag.png', ContentFile(signature_data), save=False)
            claim.save()
            send_claim_field_email(claim.tracking_number, claim.total_claim_amount, claim.id, settings.BASE_URL)
            send_claim_email_to_client(claim.tracking_number, claim.total_claim_amount, claim.id, settings.BASE_URL, claim.user.email)
            messages.success(request, 'Claim successfully submitted we will reach out as soon as we have a update.', extra_tags='success')
            return redirect('start_claim')
    
        return render(request, 'claims_app/start_claim.html', {'claim_form': claim_form})


class AdminClaimDetailView(AdminOrStaff):
    def get(self, request, claim_id):
        claim = get_object_or_404(Claim, id=claim_id)
        # insatiate the ClaimForm with all the claim data
        claim_form = ClaimForm(instance=claim)
        claim_admin_form = AdminUpdateClaimForm(initial={'status': claim.status, 'notes': claim.notes})
        return render(request, 'claims_app/admin_claim_detail.html', {'claim_form': claim_form, 'claim': claim, 'claim_admin_form': claim_admin_form})
    
    def post(self, request, claim_id):
        claim = get_object_or_404(Claim, id=claim_id)
        claim_form = ClaimForm(request.POST, instance=claim)
        claim_admin_form = AdminUpdateClaimForm(request.POST, initial={'status': claim.status, 'notes': claim.notes})
       
        
        if 'status' in request.POST:
            if claim_admin_form.is_valid():
                claim.notes = claim_admin_form.cleaned_data['notes']
                claim.status = claim_admin_form.cleaned_data['status']
                claim.save()
                messages.success(request, 'Claim successfully Updated', extra_tags='success')
                return redirect('admin_claim_detail', claim_id=claim_id)
        if 'email' in request.POST:
            if claim_form.is_valid():
                claim_form.save()
    
                messages.success(request, 'Claim successfully Updated', extra_tags='success')
                return redirect('admin_claim_detail', claim_id=claim_id)
        
        return render(request, 'claims_app/admin_claim_detail.html', {'claim_form': claim_form, 'claim': claim, 'claim_admin_form': claim_admin_form})
      
    

    
class AdminClaimListView(AdminOrStaff):
    def get(self, request):
        claims = Claim.objects.all()
      
        return render(request, 'claims_app/admin_claim_list.html', {'claims': claims})
    
    def post(self, request):
        claims = Claim.objects.all()
        return render(request, 'claims_app/admin_claim_list.html', {'claims': claims})