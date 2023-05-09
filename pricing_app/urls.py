from django.urls import path
from . import views 

app_name = 'pricing_app'

quote = [
    path('quote/', views.Quote.as_view(), name='quote'),
    path('pricing/', views.pricing, name='pricing'),
    path('download_template/', views.download_template_file, name='download_shipments_template'),
    path('download_sample/', views.download_sample_file, name='download_shipments_sample'),
    path('upload_file/', views.upload_file, name='upload_shipments_file'),
    path('upload_breakdown/<uuid:file_id>/', views.UploadBreakdown.as_view(), name='upload_breakdown'),
    path('download_shipments_with_pricing/<uuid:file_id>/', views.download_shipments_file_with_pricing, name='download_shipments_with_pricing'),
    path('about/', views.about, name='about'),
    path('create_rate_card/', views.CreateRateCardView.as_view(), name='create_rate_card'),
    path('rate_cards/', views.RateCardListView.as_view(), name='rate_cards'),
    path('rate_card/<uuid:rate_card_id>/', views.RateCardDetailView.as_view(), name='rate_card_detail'),
    path('create_rate_card_item_for/<uuid:rate_card_id>/', views.CreateRateCardItemView.as_view(), name='create_rate_card_item'),
    path('delete_rate_card_item/<uuid:rate_card_item_id>/<uuid:rate_card_id>/', views.DeleteRateCardItemView.as_view(), name='delete_rate_card_item'),
    path('', views.home, name='home'),
]


urlpatterns = [
   *quote,
]