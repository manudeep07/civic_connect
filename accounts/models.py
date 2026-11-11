from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Citizen / Student'),
        ('university', 'University'),
        ('industry', 'Industry'),
        ('admin', 'Administrator'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text="Designated role for platform access and permissions"
    )
    institution_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="University, college, organization, or company name"
    )
    location = models.CharField(
        max_length=150,
        blank=True,
        help_text="City, State, Country"
    )
    bio = models.TextField(
        blank=True,
        help_text="Brief professional or individual summary"
    )
    phone = models.CharField(
        max_length=25,
        blank=True,
        help_text="Contact telephone number"
    )
    website = models.URLField(
        blank=True,
        help_text="Official institution, company, or personal portfolio URL"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        display = self.get_full_name() or self.username
        if self.institution_name:
            return f"{display} ({self.institution_name}) [{self.get_role_display()}]"
        return f"{display} [{self.get_role_display()}]"

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_university(self):
        return self.role == 'university'

    @property
    def is_industry(self):
        return self.role == 'industry'

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    def get_role_badge_class(self):
        badge_map = {
            'student': 'bg-primary',
            'university': 'bg-success',
            'industry': 'bg-info text-dark',
            'admin': 'bg-danger',
        }
        return badge_map.get(self.role, 'bg-secondary')


class Activity(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=50,
        help_text="Type of activity, e.g., 'challenge_created', 'solution_submitted'"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
