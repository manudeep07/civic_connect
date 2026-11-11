from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Activity


def log_activity(user, activity_type, title, description='', link=''):
    """
    Utility function to record user activity feed events.
    """
    if user and user.is_authenticated:
        Activity.objects.create(
            user=user,
            activity_type=activity_type,
            title=title,
            description=description,
            link=link
        )


def role_required(allowed_roles):
    """
    Decorator for views that checks if the logged-in user possesses one of the allowed roles.
    Demonstrates INT253 CO6 (Session & Authentication Control).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Access restricted: You do not have permissions for this section.")
            return redirect('dashboard:index')
        return _wrapped_view
    return decorator

