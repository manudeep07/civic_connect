from django.contrib import admin
from .models import Project, ProjectMembership


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge', 'lead', 'status', 'progress_percentage', 'start_date', 'expected_completion_date')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'lead__username', 'challenge__title')
    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('project__title', 'user__username', 'role')
