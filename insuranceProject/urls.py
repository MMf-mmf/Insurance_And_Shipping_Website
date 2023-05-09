from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include("users_app.urls"), name="account"),
    path('payments/',include("payments_app.urls"), name="payments"),
    path('users/', include("users_app.urls"), name="users"),
    path('shipping/', include("shipping_app.urls"), name="shipping"),
    path('claims/', include("claims_app.urls"), name="claims"),
    path('', include("pricing_app.urls"), name="pricing"),
    path("__reload__/", include("django_browser_reload.urls")),
    path('__debug__/', include('debug_toolbar.urls')),
]


handler404 = 'users_app.views.handler_404'
handler500 = 'users_app.views.handler_500'


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns