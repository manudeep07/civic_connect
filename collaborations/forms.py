from django import forms
from django.contrib.auth import get_user_model
from .models import Project, ProjectMembership

User = get_user_model()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'status',
            'progress_percentage',
            'start_date',
            'expected_completion_date',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Campus Autonomous Waste Sorter Deployment'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'progress_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'State project milestones, objectives, technical architecture, and team deliverables...'
            }),
        }


class ProjectMembershipAddForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select a registered user to join this project team"
    )

    class Meta:
        model = ProjectMembership
        fields = ['user', 'role']
        widgets = {
            'role': forms.Select(choices=ProjectMembership.ROLE_CHOICES, attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            # Exclude users who are already team members
            existing_user_ids = project.memberships.values_list('user_id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_user_ids).order_by('username')

