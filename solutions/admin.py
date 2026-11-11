from django.contrib import admin
from .models import Solution


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge', 'creator', 'is_accepted', 'estimated_duration', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('title', 'description', 'creator__username', 'challenge__title')
    actions = ['mark_as_accepted', 'unmark_accepted']

    @admin.action(description="Mark selected solutions as Accepted")
    def mark_as_accepted(self, request, queryset):
        count = queryset.update(is_accepted=True)
        self.message_user(request, f"{count} solution(s) marked as accepted.")

    @admin.action(description="Revoke accepted status")
    def unmark_accepted(self, request, queryset):
        count = queryset.update(is_accepted=False)
        self.message_user(request, f"{count} solution(s) unmarked.")
