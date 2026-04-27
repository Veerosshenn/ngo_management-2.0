from django.urls import path, include
from rest_framework import routers

from .api import NGOViewSet, ActivityViewSet

router = routers.DefaultRouter()
router.register(r"ngos", NGOViewSet)
router.register(r"activities", ActivityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

