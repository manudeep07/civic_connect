from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from challenges.models import Challenge, Category, Vote, Comment
from solutions.models import Solution
from collaborations.models import Project, ProjectMembership
from partnerships.models import PartnershipRequest
from accounts.models import Activity
from accounts.utils import log_activity

User = get_user_model()


@login_required
def dashboard_index_view(request):
    """
    Role-specific dashboard routing and dynamic data loading.
    Demonstrates INT253 CO2 (Dynamic Views), CO5 (ORM Queries), and CO6 (Role Based Dashboards).
    """
    user = request.user
    role = user.role

    # Staff / Admin role dashboard
    if user.is_admin_user or role == 'admin':
        return render_admin_dashboard(request)

    # University role dashboard
    elif role == 'university':
        return render_university_dashboard(request)

    # Industry role dashboard
    elif role == 'industry':
        return render_industry_dashboard(request)

    # Default Citizen / Student dashboard
    else:
        return render_student_dashboard(request)


def render_student_dashboard(request):
    user = request.user
    my_challenges = Challenge.objects.filter(creator=user).select_related('category')
    my_solutions = Solution.objects.filter(creator=user).select_related('challenge')
    my_collaborations = ProjectMembership.objects.filter(user=user).select_related('project', 'project__challenge')
    my_votes = Vote.objects.filter(user=user).select_related('challenge', 'challenge__category')
    recent_activities = user.activities.all()[:8]

    # Dynamic metrics
    stats = {
        'total_challenges': my_challenges.count(),
        'approved_challenges': my_challenges.filter(status='approved').count(),
        'total_solutions': my_solutions.count(),
        'accepted_solutions': my_solutions.filter(is_accepted=True).count(),
        'total_projects': my_collaborations.count(),
        'total_votes': my_votes.count(),
    }

    context = {
        'stats': stats,
        'my_challenges': my_challenges[:5],
        'my_solutions': my_solutions[:5],
        'my_collaborations': my_collaborations[:5],
        'my_votes': my_votes[:5],
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


def render_university_dashboard(request):
    user = request.user
    published_challenges = Challenge.objects.filter(creator=user).select_related('category')
    associated_projects = Project.objects.filter(
        Q(lead=user) | Q(challenge__creator=user) | Q(memberships__user=user)
    ).distinct().select_related('challenge', 'lead')

    # Student solutions submitted for university challenges
    student_solutions = Solution.objects.filter(
        challenge__creator=user
    ).select_related('creator', 'challenge')

    pending_partnerships = PartnershipRequest.objects.filter(
        target_organization=user,
        status='pending'
    ).select_related('requesting_organization', 'project', 'challenge')

    recent_activities = user.activities.all()[:8]

    stats = {
        'published_challenges': published_challenges.count(),
        'active_projects': associated_projects.filter(status='active').count(),
        'received_solutions': student_solutions.count(),
        'pending_partnerships': pending_partnerships.count(),
    }

    context = {
        'stats': stats,
        'published_challenges': published_challenges[:5],
        'associated_projects': associated_projects[:5],
        'student_solutions': student_solutions[:5],
        'pending_partnerships': pending_partnerships,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/university_dashboard.html', context)


def render_industry_dashboard(request):
    user = request.user
    interested_projects = Project.objects.filter(
        Q(lead=user) | Q(memberships__user=user)
    ).distinct().select_related('challenge', 'lead')

    sent_requests = PartnershipRequest.objects.filter(
        requesting_organization=user
    ).select_related('target_organization', 'project', 'challenge')

    received_requests = PartnershipRequest.objects.filter(
        target_organization=user
    ).select_related('requesting_organization', 'project', 'challenge')

    # Recommended high-impact challenges in need of industry support
    available_challenges = Challenge.objects.filter(
        status__in=['approved', 'in_progress'],
        problem_severity__in=['high', 'critical']
    ).select_related('category', 'creator')[:6]

    recent_activities = user.activities.all()[:8]

    stats = {
        'collaborations_count': interested_projects.count(),
        'sent_partnerships': sent_requests.count(),
        'received_partnerships': received_requests.count(),
        'available_challenges_count': Challenge.objects.filter(status__in=['approved', 'in_progress']).count(),
    }

    context = {
        'stats': stats,
        'interested_projects': interested_projects[:5],
        'sent_requests': sent_requests[:5],
        'received_requests': received_requests[:5],
        'available_challenges': available_challenges,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/industry_dashboard.html', context)


def render_admin_dashboard(request):
    pending_challenges = Challenge.objects.filter(status='pending').select_related('creator', 'category')
    all_challenges = Challenge.objects.all().select_related('creator', 'category')
    recent_users = User.objects.all().order_by('-date_joined')[:6]
    recent_activities = Activity.objects.all().select_related('user').order_by('-created_at')[:8]

    stats = {
        'total_users': User.objects.count(),
        'total_challenges': Challenge.objects.count(),
        'pending_challenges_count': pending_challenges.count(),
        'approved_challenges': Challenge.objects.filter(status='approved').count(),
        'total_solutions': Solution.objects.count(),
        'total_projects': Project.objects.count(),
        'total_votes': Vote.objects.count(),
        'total_partnerships': PartnershipRequest.objects.count(),
    }

    context = {
        'stats': stats,
        'pending_challenges': pending_challenges,
        'recent_challenges': all_challenges[:6],
        'recent_users': recent_users,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def admin_approve_challenge(request, pk):
    """
    Quick 1-click approval for administrators from the dashboard.
    """
    if not request.user.is_admin_user:
        messages.error(request, "Permission denied.")
        return redirect('dashboard:index')

    challenge = get_object_or_404(Challenge, pk=pk)
    challenge.status = 'approved'
    challenge.save()

    log_activity(
        user=challenge.creator,
        activity_type='challenge_approved',
        title=f"Your challenge '{challenge.title}' was approved by administration!",
        link=f"/challenges/{challenge.pk}/"
    )

    messages.success(request, f"Challenge '{challenge.title}' is now approved and live for public view and solutions!")
    return redirect('dashboard:index')


@login_required
def admin_reject_challenge(request, pk):
    """
    Quick 1-click rejection for administrators from the dashboard.
    """
    if not request.user.is_admin_user:
        messages.error(request, "Permission denied.")
        return redirect('dashboard:index')

    challenge = get_object_or_404(Challenge, pk=pk)
    challenge.status = 'rejected'
    challenge.save()

    messages.warning(request, f"Challenge '{challenge.title}' has been marked as rejected.")
    return redirect('dashboard:index')
