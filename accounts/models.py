from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_image_file


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen / Student'),
        ('organization', 'Organization'),
        ('admin', 'Administrator'),
    )

    ORG_TYPE_CHOICES = (
        ('university', 'University'),
        ('industry', 'Industry'),
        ('government_ngo', 'Government / NGO'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='citizen',
        help_text="Designated role for platform access and permissions"
    )
    org_type = models.CharField(
        max_length=20,
        choices=ORG_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Organization type (used only when role is organization)"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this organization is verified by administrators."
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
        validators=[validate_image_file],
        help_text="Profile picture (Max 2MB, JPG/PNG/WEBP)"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        # Normalize legacy roles if passed
        if self.role == 'student':
            self.role = 'citizen'
        elif self.role == 'university':
            self.role = 'organization'
            if not self.org_type:
                self.org_type = 'university'
        elif self.role == 'industry':
            self.role = 'organization'
            if not self.org_type:
                self.org_type = 'industry'

        # Auto-verify citizens and administrators on creation; organizations require admin review
        if self._state.adding and self.is_superuser:
            self.role = 'admin'
        if self._state.adding and self.role in ['citizen', 'admin']:
            self.is_verified = True
        elif self._state.adding and self.role == 'organization':
            if self.is_verified is None:
                self.is_verified = False

        super().save(*args, **kwargs)

    def __str__(self):
        display = self.get_full_name() or self.username
        if self.institution_name:
            return f"{display} ({self.institution_name}) [{self.get_role_display()}]"
        return f"{display} [{self.get_role_display()}]"

    @property
    def is_citizen(self):
        return self.role == 'citizen'

    @property
    def is_organization(self):
        return self.role == 'organization'

    @property
    def is_student(self):
        return self.role == 'citizen'

    @property
    def is_university(self):
        return self.role == 'organization' and self.org_type == 'university'

    @property
    def is_industry(self):
        return self.role == 'organization' and self.org_type == 'industry'

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    def get_role_badge_class(self):
        badge_map = {
            'citizen': 'bg-primary',
            'organization': 'bg-success',
            'admin': 'bg-danger',
            'student': 'bg-primary',
            'university': 'bg-success',
            'industry': 'bg-info text-dark',
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


class UserScore(models.Model):
    """
    Points system for the leaderboard.
    Points are awarded for key platform actions:
      - Submitting a challenge:          10 pts
      - Getting a solution accepted:     25 pts
      - Completing a project:            50 pts
    """
    POINT_EVENTS = (
        ('challenge_created', 'Challenge Created (+10)'),
        ('solution_accepted', 'Solution Accepted (+25)'),
        ('project_completed', 'Project Completed (+50)'),
    )

    POINTS_MAP = {
        'challenge_created': 10,
        'solution_accepted': 25,
        'project_completed': 50,
    }

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='score_events'
    )
    event_type = models.CharField(max_length=30, choices=POINT_EVENTS)
    points = models.PositiveIntegerField(default=0)
    reference_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="PK of the related object (challenge, solution, or project)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Score Event'
        verbose_name_plural = 'User Score Events'
        ordering = ['-created_at']
        # One event per user per object reference
        unique_together = [['user', 'event_type', 'reference_id']]

    def __str__(self):
        return f"{self.user.username} +{self.points} ({self.get_event_type_display()})"

    @classmethod
    def award(cls, user, event_type, reference_id=None):
        """Award points for an event (idempotent for same user+type+ref)."""
        points = cls.POINTS_MAP.get(event_type, 0)
        if points == 0:
            return
        cls.objects.get_or_create(
            user=user,
            event_type=event_type,
            reference_id=reference_id,
            defaults={'points': points}
        )
