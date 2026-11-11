from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .utils import log_activity

User = get_user_model()


def register_view(request):
    """
    Handle user registration with custom roles, institution, and location.
    Demonstrates INT253 CO4 (Django Forms) & CO6 (Authentication).
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_activity(
                user=user,
                activity_type='user_registered',
                title=f"Welcome to CivicConnect, {user.first_name}!",
                description="Your account was successfully created.",
                link='/dashboard/'
            )
            messages.success(request, f"Welcome to CivicConnect, {user.get_full_name() or user.username}! Your account has been created.")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle authentication via username and password.
    Demonstrates INT253 CO6 (Cookies, Sessions & Authentication).
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard:index'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Log out the current user and flush session.
    Demonstrates INT253 CO6.
    """
    user_name = request.user.username
    logout(request)
    messages.info(request, f"You have been safely logged out, @{user_name}.")
    return redirect('home')


@login_required
def profile_view(request):
    """
    Display current user's profile, activity feed, and statistics.
    """
    user = request.user
    activities = user.activities.all()[:10]
    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'is_own_profile': True,
        'activities': activities
    })


def user_detail_view(request, username):
    """
    Public profile view for any community member, university, or industry partner.
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = (request.user.is_authenticated and request.user.username == username)
    activities = profile_user.activities.all()[:8]
    challenges_count = profile_user.challenges.filter(status='approved').count() if not is_own_profile else profile_user.challenges.count()
    solutions_count = profile_user.solutions.count()
    projects_count = profile_user.led_projects.count()

    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'activities': activities,
        'challenges_count': challenges_count,
        'solutions_count': solutions_count,
        'projects_count': projects_count,
    })


@login_required
def edit_profile_view(request):
    """
    Allow authenticated users to modify their personal or organization profile details.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(
                user=request.user,
                activity_type='profile_updated',
                title="Profile information updated",
                link='/accounts/profile/'
            )
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    """
    Change user password with session preservation.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
