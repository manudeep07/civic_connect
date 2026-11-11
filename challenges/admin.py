from django.contrib import admin
from .models import Category, Challenge, Vote, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'approved_challenges_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'creator', 'problem_severity', 'status', 'created_at', 'votes_count', 'solutions_count')
    list_filter = ('status', 'problem_severity', 'category', 'created_at')
    search_fields = ('title', 'description', 'location', 'creator__username', 'creator__institution_name')
    actions = ['approve_challenges', 'reject_challenges', 'mark_in_progress', 'mark_solved']

    @admin.action(description="Approve selected challenges")
    def approve_challenges(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count} challenge(s) marked as Approved.")

    @admin.action(description="Reject selected challenges")
    def reject_challenges(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} challenge(s) marked as Rejected.")

    @admin.action(description="Mark selected as In Progress")
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status='in_progress')
        self.message_user(request, f"{count} challenge(s) marked as In Progress.")

    @admin.action(description="Mark selected as Solved")
    def mark_solved(self, request, queryset):
        count = queryset.update(status='solved')
        self.message_user(request, f"{count} challenge(s) marked as Solved.")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'challenge__title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'challenge__title', 'content')
