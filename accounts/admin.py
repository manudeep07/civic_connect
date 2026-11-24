from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Activity


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'org_type', 'is_verified', 'institution_name', 'location', 'is_staff')
    list_filter = ('role', 'org_type', 'is_verified', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'institution_name', 'location')
    ordering = ('-date_joined',)
    actions = ['verify_organizations', 'unverify_organizations']

    @admin.action(description="Verify selected organizations")
    def verify_organizations(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} user(s) marked as verified.")

    @admin.action(description="Revoke verification for selected users")
    def unverify_organizations(self, request, queryset):
        count = queryset.update(is_verified=False)
        self.message_user(request, f"{count} user(s) marked as unverified.")

    fieldsets = UserAdmin.fieldsets + (
        ('CivicConnect Role & Profile', {
            'fields': ('role', 'org_type', 'is_verified', 'institution_name', 'location', 'phone', 'website', 'bio', 'avatar')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('CivicConnect Details', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'org_type', 'is_verified', 'institution_name', 'location')
        }),
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'title', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'title', 'description')
