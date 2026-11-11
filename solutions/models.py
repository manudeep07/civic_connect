from django.db import models
from django.conf import settings


class Solution(models.Model):
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.CASCADE,
        related_name='solutions'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solutions'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed overview of the proposed solution.")
    proposed_implementation = models.TextField(
        help_text="Step-by-step technical or operational approach."
    )
    expected_outcome = models.TextField(
        help_text="Measurable impact, key metrics, and expected results."
    )
    required_resources = models.TextField(
        help_text="Skills, hardware, software, lab equipment, or budget needed."
    )
    estimated_duration = models.CharField(
        max_length=100,
        help_text="e.g., '3 Months', '16 Weeks', '6 Months'"
    )
    is_accepted = models.BooleanField(
        default=False,
        help_text="Marked as accepted by the challenge creator or university/admin"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
        ordering = ['-is_accepted', '-created_at']

    def __str__(self):
        return f"{self.title} (for {self.challenge.title})"

    @property
    def has_project(self):
        return self.projects.exists()
