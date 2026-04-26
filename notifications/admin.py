from django.contrib import admin
from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'message_preview', 'is_read', 'sent_at']
    list_filter = ['is_read']
    search_fields = ['recipient__username', 'message']
    readonly_fields = ['sent_at']

    def message_preview(self, obj):
        return obj.message[:60] + '...' if len(obj.message) > 60 else obj.message
    message_preview.short_description = 'Message'
