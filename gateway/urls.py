from django.urls import path, re_path

from gateway import views

urlpatterns = [
    path("gateway/register/", views.register_orchestrated, name="gw_register"),
    re_path(r"^gw/(?P<service>user|ngo|reg)/(?P<path>.*)$", views.proxy, name="gw_proxy"),
]

