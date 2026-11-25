from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from challenges.models import Challenge, Category, Vote, Comment
from solutions.models import Solution
from collaborations.models import Project, ProjectMembership
from accounts.models import Activity
from accounts.utils import log_activity

User = get_user_model()


@login_required
def dashboard_index_view(request):
    """
    Role-specific dashboard routing and dynamic data loading.
    """
    user = request.user
    role = user.role

    # Staff / Admin role dashboard
    if user.is_admin_user or role == 'admin':
        return render_admin_dashboard(request)

    # Organization dashboard (unified for university, industry, government/ngo)
    elif role == 'organization' or role in ['university', 'industry']:
        return render_organization_dashboard(request)

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


def render_organization_dashboard(request):
    """
    Merged dashboard for all organizations:
    - Assigned / published challenges
    - My solutions (submitted by organization or received on organization challenges)
    - Sponsored pilots
    """
    user = request.user

    # Assigned or created challenges by this organization
    if user.institution_name:
        assigned_challenges = Challenge.objects.filter(
            Q(creator=user) | Q(organization_name__icontains=user.institution_name)
        ).distinct().select_related('category', 'creator')
    else:
        assigned_challenges = Challenge.objects.filter(creator=user).select_related('category', 'creator')

    # Solutions submitted by this organization
    my_solutions = Solution.objects.filter(creator=user).select_related('challenge')

    # Solutions received on challenges created by this organization
    received_solutions = Solution.objects.filter(
        challenge__creator=user
    ).select_related('creator', 'challenge')

    # Sponsored pilot initiatives
    sponsored_pilots = Project.objects.filter(
        pilot_sponsor=user
    ).select_related('challenge', 'lead')

    # Associated projects led or collaborated on
    associated_projects = Project.objects.filter(
        Q(lead=user) | Q(memberships__user=user)
    ).distinct().select_related('challenge', 'lead')

    # Recommended high-impact challenges in need of support
    available_challenges = Challenge.objects.filter(
        status__in=['approved', 'in_progress'],
        problem_severity__in=['high', 'critical']
    ).select_related('category', 'creator')[:6]

    recent_activities = user.activities.all()[:8]

    stats = {
        'assigned_challenges_count': assigned_challenges.count(),
        'my_solutions_count': my_solutions.count(),
        'received_solutions_count': received_solutions.count(),
        'sponsored_pilots_count': sponsored_pilots.count(),
        'associated_projects_count': associated_projects.count(),
    }

    context = {
        'stats': stats,
        'assigned_challenges': assigned_challenges[:6],
        'my_solutions': my_solutions[:6],
        'received_solutions': received_solutions[:6],
        'sponsored_pilots': sponsored_pilots[:6],
        'associated_projects': associated_projects[:6],
        'available_challenges': available_challenges,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/organization_dashboard.html', context)


# Backwards compatibility aliases
render_university_dashboard = render_organization_dashboard
render_industry_dashboard = render_organization_dashboard
render_citizen_dashboard = render_student_dashboard


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
@require_POST
def admin_approve_challenge(request, pk):
    """
    POST-only: Approve a challenge from the admin dashboard.
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
@require_POST
def admin_reject_challenge(request, pk):
    """
    POST-only: Reject a challenge from the admin dashboard.
    """
    if not request.user.is_admin_user:
        messages.error(request, "Permission denied.")
        return redirect('dashboard:index')

    challenge = get_object_or_404(Challenge, pk=pk)
    challenge.status = 'rejected'
    challenge.save()

    messages.warning(request, f"Challenge '{challenge.title}' has been marked as rejected.")
    return redirect('dashboard:index')


import json
from accounts.models import UserScore
from django.db.models import Sum


@login_required
def analytics_view(request):
    """
    Analytics dashboard with Chart.js charts.
    Accessible to admins and verified organizations.
    """
    user = request.user
    if not (user.is_admin_user or (user.role in ['organization', 'university', 'industry'] and user.is_verified)):
        messages.error(request, "Analytics is available to administrators and verified partners.")
        return redirect('dashboard:index')

    # Challenges by category
    by_category = list(
        Challenge.objects.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # Challenges by status
    by_status = list(
        Challenge.objects.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Challenges by location (top 10)
    by_location = list(
        Challenge.objects.values('location')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # Solutions per challenge (top 10)
    from solutions.models import Solution
    solutions_per_challenge = list(
        Challenge.objects.filter(status__in=['approved', 'in_progress', 'solved'])
        .annotate(sol_count=Count('solutions'))
        .values('title', 'sol_count')
        .order_by('-sol_count')[:10]
    )

    summary = {
        'total_challenges': Challenge.objects.count(),
        'total_solutions': Solution.objects.count(),
        'total_projects': Project.objects.count(),
        'total_users': User.objects.count(),
        'approved': Challenge.objects.filter(status='approved').count(),
        'in_progress': Challenge.objects.filter(status='in_progress').count(),
        'solved': Challenge.objects.filter(status='solved').count(),
    }

    return render(request, 'dashboard/analytics.html', {
        'by_category_json': json.dumps(by_category),
        'by_status_json': json.dumps(by_status),
        'by_location_json': json.dumps(by_location),
        'solutions_per_challenge_json': json.dumps(solutions_per_challenge),
        'summary': summary,
    })


@login_required
def leaderboard_view(request):
    """
    Leaderboard of top contributors by points.
    Points: challenge_created=10, solution_accepted=25, project_completed=50.
    """
    top_users = (
        User.objects
        .filter(score_events__isnull=False)
        .annotate(total_points=Sum('score_events__points'))
        .order_by('-total_points')[:20]
    )

    # Also get current user's rank
    user_points = UserScore.objects.filter(user=request.user).aggregate(total=Sum('points'))['total'] or 0

    return render(request, 'dashboard/leaderboard.html', {
        'top_users': top_users,
        'user_points': user_points,
    })
