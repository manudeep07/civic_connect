from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .validators import validate_image_file

User = get_user_model()

PUBLIC_ROLE_CHOICES = (
    ('student', 'Citizen / Student'),
    ('university', 'University'),
    ('industry', 'Industry'),
)


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    role = forms.ChoiceField(
        choices=PUBLIC_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}),
        help_text="At least 8 characters"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'institution_name',
            'location',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'institution_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University, College, or Company name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chicago, IL or Mumbai, India'}),
        }

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['student', 'university', 'industry']:
            raise ValidationError("Administrator accounts cannot be registered publicly.")
        return role

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        institution = cleaned_data.get("institution_name")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if role == 'student':
            if not cleaned_data.get('first_name'):
                self.add_error('first_name', "First name is required for Student accounts.")
            if not cleaned_data.get('last_name'):
                self.add_error('last_name', "Last name is required for Student accounts.")

        if role in ['university', 'industry'] and not institution:
            self.add_error('institution_name', f"Institution/Company name is required for {role.capitalize()} role.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'institution_name',
            'location',
            'phone',
            'website',
            'bio',
            'avatar',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'institution_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'file'):
            validate_image_file(avatar)
        return avatar

