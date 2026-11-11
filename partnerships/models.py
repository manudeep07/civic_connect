from django.db import models
from django.conf import settings


class PartnershipRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Declined'),
    )

    PARTNERSHIP_TYPES = (
        ('mentorship', 'Mentorship & Academic Guidance'),
        ('technical', 'Technical & R&D Expertise'),
        ('sponsorship', 'Resource / Lab Sponsorship'),
        ('student_internship', 'Student Placement & Training'),
        ('general_collaboration', 'Strategic Partnership'),
    )

    requesting_organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_partnership_requests',
        help_text="Organization or user initiating this partnership proposal"
    )
    target_organization = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_partnership_requests',
        help_text="Target University or Industry partner"
    )
    project = models.ForeignKey(
        'collaborations.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partnership_requests',
        help_text="Associated collaborative project if applicable"
    )
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partnership_requests',
        help_text="Associated societal challenge if applicable"
    )
    partnership_type = models.CharField(
        max_length=50,
        choices=PARTNERSHIP_TYPES,
        default='mentorship'
    )
    message = models.TextField(help_text="State proposed collaboration objectives, roles, and scope.")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    response_note = models.TextField(
        blank=True,
        help_text="Optional remarks or meeting invite from target organization"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Partnership Request'
        verbose_name_plural = 'Partnership Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Partnership from {self.requesting_organization.display_name} to {self.target_organization.display_name} ({self.get_status_display()})"

    def get_status_badge_class(self):
        classes = {
            'pending': 'bg-warning text-dark',
            'accepted': 'bg-success',
            'rejected': 'bg-danger',
        }
        return classes.get(self.status, 'bg-secondary')
