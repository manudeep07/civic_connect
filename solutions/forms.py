from django import forms
from .models import Solution


class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = [
            'title',
            'estimated_duration',
            'description',
            'proposed_implementation',
            'expected_outcome',
            'required_resources',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Solar-Powered Micro-Cold Storage with IoT Monitoring'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3 Months, 16 Weeks, 6 Months'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'High-level concept, novelty, and theoretical foundation of your solution...'
            }),
            'proposed_implementation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Step-by-step roadmap: architecture, prototyping, deployment phases...'
            }),
            'expected_outcome': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Specific expected performance milestones, social metric improvements...'
            }),
            'required_resources': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List materials, software frameworks, hardware kits, team roles, or budget estimate...'
            }),
        }

