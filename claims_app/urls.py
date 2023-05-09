from django.urls import path
from . import views

urlpatterns = [
    path('', views.StartClaimView.as_view(), name='start_claim'),
    path('admin_claim/<uuid:claim_id>/', views.AdminClaimDetailView.as_view(), name='admin_claim_detail'),
    path('admin_claims_list/', views.AdminClaimListView.as_view(), name='admin_claim_list'),
]
