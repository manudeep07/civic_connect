from django import forms
from django.contrib.auth import get_user_model
from .models import PartnershipRequest
from collaborations.models import Project
from challenges.models import Challenge

User = get_user_model()


class PartnershipRequestForm(forms.ModelForm):
    target_organization = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['university', 'industry']),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Choose an affiliated University or Industry partner to connect with"
    )

    class Meta:
        model = PartnershipRequest
        fields = [
            'target_organization',
            'partnership_type',
            'project',
            'challenge',
            'message',
        ]
        widgets = {
            'partnership_type': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'challenge': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Explain your value proposition, collaboration objectives, timeline, or mentorship offer...'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Prevent requesting partnership to oneself
            self.fields['target_organization'].queryset = User.objects.filter(
                role__in=['university', 'industry']
            ).exclude(id=user.id).order_by('institution_name', 'username')

            # Optional: Limit projects to user's projects or active projects
            self.fields['project'].queryset = Project.objects.filter(status__in=['planning', 'active']).order_by('-created_at')
            self.fields['challenge'].queryset = Challenge.objects.filter(status__in=['approved', 'in_progress']).order_by('-created_at')


class PartnershipResponseForm(forms.ModelForm):
    class Meta:
        model = PartnershipRequest
        fields = ['status', 'response_note']
        widgets = {
            'status': forms.Select(choices=[('accepted', 'Accept Partnership'), ('rejected', 'Decline')], attrs={'class': 'form-select'}),
            'response_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Provide feedback, meeting schedule, or next collaborative action steps...'
            }),
        }

