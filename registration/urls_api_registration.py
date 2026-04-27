from django.urls import path, include
from rest_framework import routers

from registration.api import RegistrationViewSet

router = routers.DefaultRouter()
router.register(r"registrations", RegistrationViewSet, basename="registrations")

urlpatterns = [
    path("", include(router.urls)),
]

