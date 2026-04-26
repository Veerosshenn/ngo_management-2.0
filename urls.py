from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('ngo/', include('ngo.urls')),
    path('registration/', include('registration.urls')),
    # API v1
    path('api/v1/', include('ngo.urls_api')),
]