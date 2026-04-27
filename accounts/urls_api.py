from django.urls import path
from rest_framework.authtoken import views as drf_auth_views

from accounts import api

app_name = "accounts_api"

urlpatterns = [
    path("auth/token/", drf_auth_views.obtain_auth_token, name="api_token_auth"),
    path("users/me/", api.me, name="me"),
]

