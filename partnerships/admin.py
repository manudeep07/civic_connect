from django.contrib import admin
from .models import PartnershipRequest


@admin.register(PartnershipRequest)
class PartnershipRequestAdmin(admin.ModelAdmin):
    list_display = ('requesting_organization', 'target_organization', 'partnership_type', 'status', 'created_at')
    list_filter = ('partnership_type', 'status', 'created_at')
    search_fields = ('requesting_organization__username', 'target_organization__username', 'message')
