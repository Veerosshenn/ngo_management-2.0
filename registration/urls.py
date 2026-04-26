from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('register/<int:activity_id>/', views.register_activity, name='register_activity'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('qr-checkin/', views.qr_checkin, name='qr_checkin'),
    path('checkin/<str:token>/', views.checkin_token, name='checkin_token'),
    path('cancel/<int:activity_id>/', views.cancel_activity, name='cancel_activity'),
]