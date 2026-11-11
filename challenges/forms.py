from django import forms
from .models import Challenge, Comment


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            'title',
            'category',
            'location',
            'problem_severity',
            'description',
            'expected_impact',
            'organization_name',
            'image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Plastic Waste Accumulation in Coastal Fisheries'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Kochi Harbor, Kerala, India'
            }),
            'problem_severity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Explain the root problem, affected demographic, and why current measures are insufficient...'
            }),
            'expected_impact': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe measurable benefits if this challenge is solved (e.g. 50% waste reduction, 1,200 households empowered)...'
            }),
            'organization_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional affiliated university, NGO, or municipal body'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your constructive perspective, potential ideas, or query...'
            })
        }
        labels = {
            'content': ''
        }

