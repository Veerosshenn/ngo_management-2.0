from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as drf_auth_views
from .api import NGOViewSet, ActivityViewSet
from registration.api import RegistrationViewSet

router = routers.DefaultRouter()
router.register(r'ngos', NGOViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'registrations', RegistrationViewSet, basename='registrations')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', drf_auth_views.obtain_auth_token, name='api_token_auth'),
]
