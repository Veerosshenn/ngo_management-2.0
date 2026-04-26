"""
ngo/admin.py  –  Django admin registrations for NGO and Activity models.

Topic 4.4 – table generation evidence (visible in /admin/)
Topic 5.1 – all entities registered so admin can inspect the schema
"""

from django.contrib import admin
from ngo.models import NGO, Activity


@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display   = ('name', 'contact_email', 'website', 'created_at')
    search_fields  = ('name', 'contact_email')
    ordering       = ('name',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display  = ('title', 'ngo', 'date', 'cut_off_datetime', 'max_slots', 'created_by')
    list_filter   = ('ngo', 'date')
    search_fields = ('title', 'location')
    raw_id_fields = ('created_by',)
    date_hierarchy = 'date'
