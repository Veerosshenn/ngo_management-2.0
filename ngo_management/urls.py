from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('ngo/', include('ngo.urls')),
    path('registration/', include('registration.urls')),
    path('notifications/', include('notifications.urls')),
    # Topic 8: RESTful APIs
    path('api/v1/', include('ngo.urls_api')),
    # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redirect root to activity list
    path('', lambda request: redirect('ngo:activity_list')),
]
