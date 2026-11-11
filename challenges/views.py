from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import HttpResponseForbidden

from .models import Challenge, Category, Vote, Comment
from .forms import ChallengeForm, CommentForm
from accounts.utils import log_activity


def challenge_list_view(request):
    """
    Browse challenges with multi-criteria search, category filters, sorting, and pagination.
    Demonstrates INT253 CO2 (Views & HTTP GET) & CO5 (Django ORM Queries & Aggregations).
    """
    # Public view shows approved, in-progress, and solved challenges
    queryset = Challenge.objects.filter(status__in=['approved', 'in_progress', 'solved'])

    # Search keyword
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q) |
            Q(organization_name__icontains=q)
        )

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        queryset = queryset.filter(category=selected_category)

    # Severity filter
    severity = request.GET.get('severity', '').strip()
    if severity in ['low', 'medium', 'high', 'critical']:
        queryset = queryset.filter(problem_severity=severity)

    # Status filter
    status = request.GET.get('status', '').strip()
    if status in ['approved', 'in_progress', 'solved']:
        queryset = queryset.filter(status=status)

    # Sorting
    sort = request.GET.get('sort', 'latest')
    if sort == 'popular':
        queryset = queryset.annotate(vote_total=Count('votes')).order_by('-vote_total', '-created_at')
    elif sort == 'solutions':
        queryset = queryset.annotate(sol_total=Count('solutions')).order_by('-sol_total', '-created_at')
    elif sort == 'oldest':
        queryset = queryset.order_by('created_at')
    else:
        # Default latest
        queryset = queryset.order_by('-created_at')

    # Pagination: 6 items per page
    paginator = Paginator(queryset, 6)
    page = request.GET.get('page', 1)
    try:
        challenges_page = paginator.page(page)
    except PageNotAnInteger:
        challenges_page = paginator.page(1)
    except EmptyPage:
        challenges_page = paginator.page(paginator.num_pages)

    categories = Category.objects.all()

    context = {
        'challenges': challenges_page,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': q,
        'selected_severity': severity,
        'selected_status': status,
        'selected_sort': sort,
        'total_results': queryset.count(),
    }
    return render(request, 'challenges/challenge_list.html', context)


def challenge_detail_view(request, pk):
    """
    Detailed challenge view, including proposed solutions, votes, and community comments.
    Demonstrates INT253 CO3 (Templates) and CO5 (ORM Relationships).
    """
    challenge = get_object_or_404(Challenge, pk=pk)

    # If pending or rejected, only creator or staff/admin can view
    if challenge.status in ['pending', 'rejected']:
        if not (request.user.is_authenticated and (request.user == challenge.creator or request.user.is_admin_user)):
            messages.warning(request, "This challenge is currently undergoing administrative review.")
            return redirect('challenges:list')

    user_has_upvoted = False
    if request.user.is_authenticated:
        user_has_upvoted = challenge.is_upvoted_by(request.user)

    comment_form = CommentForm()
    comments = challenge.comments.select_related('user').all()
    solutions = challenge.solutions.select_related('creator').all()
    projects = challenge.projects.select_related('lead').all()

    context = {
        'challenge': challenge,
        'user_has_upvoted': user_has_upvoted,
        'comment_form': comment_form,
        'comments': comments,
        'solutions': solutions,
        'projects': projects,
    }
    return render(request, 'challenges/challenge_detail.html', context)


@login_required
def challenge_create_view(request):
    """
    Submit a societal challenge.
    Demonstrates INT253 CO4 (Form Handling & Validation).
    """
    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.creator = request.user

            # If user is admin or university, automatically approve, else pending review
            if request.user.is_admin_user or request.user.is_university:
                challenge.status = 'approved'
                messages.success(request, f"Challenge '{challenge.title}' published successfully!")
            else:
                challenge.status = 'pending'
                messages.success(request, f"Challenge '{challenge.title}' submitted! It is now pending administrator review.")

            challenge.save()

            log_activity(
                user=request.user,
                activity_type='challenge_created',
                title=f"Submitted challenge: {challenge.title}",
                link=f"/challenges/{challenge.pk}/"
            )

            return redirect('challenges:detail', pk=challenge.pk)
        else:
            messages.error(request, "Please check the form fields and rectify errors.")
    else:
        form = ChallengeForm()

    return render(request, 'challenges/challenge_form.html', {
        'form': form,
        'action_title': 'Submit a Societal Challenge',
        'is_edit': False
    })


@login_required
def challenge_edit_view(request, pk):
    """
    Edit challenge details (restricted to challenge author or admin).
    """
    challenge = get_object_or_404(Challenge, pk=pk)

    if not (request.user == challenge.creator or request.user.is_admin_user):
        messages.error(request, "You are not authorized to edit this challenge.")
        return redirect('challenges:detail', pk=challenge.pk)

    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES, instance=challenge)
        if form.is_valid():
            form.save()
            log_activity(
                user=request.user,
                activity_type='challenge_updated',
                title=f"Updated challenge: {challenge.title}",
                link=f"/challenges/{challenge.pk}/"
            )
            messages.success(request, "Challenge details updated successfully.")
            return redirect('challenges:detail', pk=challenge.pk)
        else:
            messages.error(request, "Please rectify the errors indicated below.")
    else:
        form = ChallengeForm(instance=challenge)

    return render(request, 'challenges/challenge_form.html', {
        'form': form,
        'challenge': challenge,
        'action_title': 'Edit Challenge',
        'is_edit': True
    })


@login_required
def challenge_delete_view(request, pk):
    """
    Delete a challenge (restricted to author or admin).
    """
    challenge = get_object_or_404(Challenge, pk=pk)

    if not (request.user == challenge.creator or request.user.is_admin_user):
        messages.error(request, "You do not have permission to delete this challenge.")
        return redirect('challenges:detail', pk=challenge.pk)

    if request.method == 'POST':
        title = challenge.title
        challenge.delete()
        log_activity(
            user=request.user,
            activity_type='challenge_deleted',
            title=f"Deleted challenge: {title}"
        )
        messages.success(request, f"Challenge '{title}' has been successfully deleted.")
        return redirect('challenges:list')

    return render(request, 'challenges/challenge_confirm_delete.html', {'challenge': challenge})


@login_required
def vote_toggle_view(request, pk):
    """
    Toggle upvote for a challenge.
    Enforces one vote per user constraint.
    """
    challenge = get_object_or_404(Challenge, pk=pk)

    if request.method == 'POST':
        existing_vote = Vote.objects.filter(user=request.user, challenge=challenge).first()
        if existing_vote:
            existing_vote.delete()
            messages.info(request, f"Upvote removed from '{challenge.title}'.")
        else:
            Vote.objects.create(user=request.user, challenge=challenge)
            log_activity(
                user=request.user,
                activity_type='voted',
                title=f"Upvoted challenge: {challenge.title}",
                link=f"/challenges/{challenge.pk}/"
            )
            messages.success(request, f"Thank you for upvoting '{challenge.title}'!")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or f'/challenges/{pk}/'
    return redirect(next_url)


@login_required
def comment_add_view(request, pk):
    """
    Add constructive feedback comment to a challenge.
    """
    challenge = get_object_or_404(Challenge, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.challenge = challenge
            comment.save()

            log_activity(
                user=request.user,
                activity_type='commented',
                title=f"Commented on challenge: {challenge.title}",
                link=f"/challenges/{challenge.pk}/#comments"
            )
            messages.success(request, "Your comment has been posted.")
        else:
            messages.error(request, "Comment cannot be empty.")

    return redirect(f'/challenges/{pk}/#comments')


@login_required
def comment_delete_view(request, pk):
    """
    Delete a user's own comment.
    """
    comment = get_object_or_404(Comment, pk=pk)
    challenge_pk = comment.challenge.pk

    if not (request.user == comment.user or request.user.is_admin_user):
        messages.error(request, "You are not authorized to delete this comment.")
        return redirect(f'/challenges/{challenge_pk}/#comments')

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment successfully deleted.")

    return redirect(f'/challenges/{challenge_pk}/#comments')
