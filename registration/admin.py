from django.contrib import admin
from registration.models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'activity', 'status', 'registered_at']
    list_filter = ['status', 'activity']
    search_fields = ['employee__username', 'activity__title']
    readonly_fields = ['registered_at']
