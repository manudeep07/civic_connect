from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    STATUS_CHOICES = (
        ('planning', 'Planning & Scoping'),
        ('active', 'Active & In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Successfully Completed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed objective and scope of this collaborative initiative.")
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.CASCADE,
        related_name='projects'
    )
    solution = models.ForeignKey(
        'solutions.Solution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='led_projects'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Current progress from 0% to 100%"
    )
    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Collaborative Project'
        verbose_name_plural = 'Collaborative Projects'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def team_count(self):
        return self.memberships.count()

    def get_status_badge_class(self):
        classes = {
            'planning': 'bg-secondary',
            'active': 'bg-primary',
            'on_hold': 'bg-warning text-dark',
            'completed': 'bg-success',
        }
        return classes.get(self.status, 'bg-dark')

    def is_member(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.memberships.filter(user=user).exists()


class ProjectMembership(models.Model):
    ROLE_CHOICES = (
        ('Project Lead', 'Project Lead'),
        ('Student Researcher', 'Student Researcher'),
        ('Student Developer', 'Student Developer'),
        ('Faculty Mentor', 'Faculty Mentor'),
        ('Industry Advisor', 'Industry Advisor'),
        ('Community Representative', 'Community Representative'),
        ('Contributor', 'Contributor'),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(
        max_length=100,
        default='Contributor',
        help_text="Designated functional role within the project"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'
        constraints = [
            models.UniqueConstraint(fields=['project', 'user'], name='unique_project_user_membership')
        ]
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.project.title}"
