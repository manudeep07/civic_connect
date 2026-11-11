from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        default='bi-folder',
        help_text="Bootstrap icon class name, e.g. bi-tree, bi-hospital, bi-book"
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def approved_challenges_count(self):
        return self.challenges.filter(status__in=['approved', 'in_progress', 'solved']).count()


class Challenge(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Provide a clear, detailed explanation of the societal problem.")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='challenges'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenges'
    )
    location = models.CharField(
        max_length=150,
        help_text="City, Region, or Target Community affected"
    )
    problem_severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    expected_impact = models.TextField(
        help_text="Anticipated benefits and outcome if this challenge is resolved."
    )
    image = models.ImageField(
        upload_to='challenges/',
        blank=True,
        null=True,
        help_text="Optional photograph or illustration depicting the issue"
    )
    organization_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional affiliated university, NGO, or community group"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def votes_count(self):
        return self.votes.count()

    @property
    def solutions_count(self):
        return self.solutions.count()

    @property
    def projects_count(self):
        return self.projects.count()

    def is_upvoted_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()

    def get_severity_badge_class(self):
        classes = {
            'low': 'bg-info text-dark',
            'medium': 'bg-primary',
            'high': 'bg-warning text-dark',
            'critical': 'bg-danger',
        }
        return classes.get(self.problem_severity, 'bg-secondary')

    def get_status_badge_class(self):
        classes = {
            'pending': 'bg-warning text-dark',
            'approved': 'bg-success',
            'in_progress': 'bg-info text-dark',
            'solved': 'bg-primary',
            'rejected': 'bg-danger',
        }
        return classes.get(self.status, 'bg-secondary')


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        constraints = [
            models.UniqueConstraint(fields=['user', 'challenge'], name='unique_user_challenge_vote')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} upvoted {self.challenge.title}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(help_text="Write your constructive thoughts or feedback...")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.challenge.title}"
