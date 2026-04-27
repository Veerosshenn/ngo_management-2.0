from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('unread/', views.unread_status, name='unread_status'),
    path('<int:notification_id>/read/', views.mark_read, name='mark_read'),
    path('read-all/', views.mark_all_read, name='mark_all_read'),
]
