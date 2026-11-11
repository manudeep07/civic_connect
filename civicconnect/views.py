from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count

from challenges.models import Challenge, Category
from solutions.models import Solution
from collaborations.models import Project

User = get_user_model()


def home_view(request):
    """
    CivicConnect Landing Page.
    Fetches real-time dynamic statistics, featured challenges, partnerships, and impact metrics.
    Demonstrates INT253 CO2 (Views & Context) and CO5 (ORM Queries).
    """
    # Featured challenges (approved/in_progress, ordered by votes & recency)
    featured_challenges = Challenge.objects.filter(
        status__in=['approved', 'in_progress', 'solved']
    ).select_related('category', 'creator').annotate(
        vote_total=Count('votes')
    ).order_by('-vote_total', '-created_at')[:3]

    # Categories with count
    categories = Category.objects.all()[:8]

    # Partner institutions
    featured_universities = User.objects.filter(role='university')[:4]
    featured_industries = User.objects.filter(role='industry')[:4]

    # Active collaborative projects
    active_projects = Project.objects.filter(
        status__in=['active', 'completed']
    ).select_related('challenge', 'lead')[:3]

    # Dynamic platform statistics
    stats = {
        'total_challenges': Challenge.objects.filter(status__in=['approved', 'in_progress', 'solved']).count(),
        'total_solutions': Solution.objects.count(),
        'total_projects': Project.objects.count(),
        'total_partners': User.objects.filter(role__in=['university', 'industry']).count(),
    }

    context = {
        'featured_challenges': featured_challenges,
        'categories': categories,
        'featured_universities': featured_universities,
        'featured_industries': featured_industries,
        'active_projects': active_projects,
        'stats': stats,
    }
    return render(request, 'home.html', context)


def about_view(request):
    """
    About CivicConnect & INT253 Academic Course Project overview.
    """
    return render(request, 'about.html')

