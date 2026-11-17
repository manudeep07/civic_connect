from django import forms
from .models import Challenge, Comment
from accounts.validators import validate_image_file


class ChallengeForm(forms.ModelForm):
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Challenge
        fields = [
            'title',
            'category',
            'location',
            'latitude',
            'longitude',
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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'file'):
            validate_image_file(image)
        return image

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')

        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise forms.ValidationError("Both latitude and longitude must be provided together, or both left blank.")

        if lat is not None:
            if not (-90.0 <= lat <= 90.0):
                self.add_error('latitude', "Latitude must be between -90 and 90 degrees.")
        if lng is not None:
            if not (-180.0 <= lng <= 180.0):
                self.add_error('longitude', "Longitude must be between -180 and 180 degrees.")

        return cleaned_data


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

