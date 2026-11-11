from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Activity


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'institution_name', 'location', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'institution_name', 'location')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('CivicConnect Role & Profile', {
            'fields': ('role', 'institution_name', 'location', 'phone', 'website', 'bio', 'avatar')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('CivicConnect Details', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'institution_name', 'location')
        }),
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'title', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'title', 'description')
