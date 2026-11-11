from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Project, ProjectMembership
from .forms import ProjectForm, ProjectMembershipAddForm
from solutions.models import Solution
from challenges.models import Challenge
from accounts.utils import log_activity


def project_list_view(request):
    """
    Browse collaborative projects with status filters and keyword search.
    Demonstrates INT253 CO2 and CO5.
    """
    projects = Project.objects.select_related('challenge', 'solution', 'lead').prefetch_related('memberships__user')

    q = request.GET.get('q', '').strip()
    if q:
        projects = projects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(challenge__title__icontains=q) |
            Q(lead__username__icontains=q) |
            Q(lead__institution_name__icontains=q)
        )

    status = request.GET.get('status', '').strip()
    if status in ['planning', 'active', 'on_hold', 'completed']:
        projects = projects.filter(status=status)

    paginator = Paginator(projects, 6)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)

    context = {
        'projects': projects_page,
        'search_query': q,
        'selected_status': status,
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='active').count(),
        'completed_projects': Project.objects.filter(status='completed').count(),
    }
    return render(request, 'collaborations/project_list.html', context)


def project_detail_view(request, pk):
    """
    Detailed collaborative workspace showing team, progress, challenge, and milestones.
    """
    project = get_object_or_404(
        Project.objects.select_related('challenge', 'solution', 'lead'),
        pk=pk
    )
    memberships = project.memberships.select_related('user').all()
    is_lead = (request.user.is_authenticated and (request.user == project.lead or request.user.is_admin_user))
    is_member = (request.user.is_authenticated and project.is_member(request.user))

    member_form = ProjectMembershipAddForm(project=project) if is_lead else None
    partnership_requests = project.partnership_requests.all() if (is_lead or request.user.is_university or request.user.is_industry) else []

    context = {
        'project': project,
        'memberships': memberships,
        'is_lead': is_lead,
        'is_member': is_member,
        'member_form': member_form,
        'partnership_requests': partnership_requests,
    }
    return render(request, 'collaborations/project_detail.html', context)


@login_required
def project_create_from_solution_view(request, solution_id):
    """
    Launch a collaborative project from an accepted solution.
    Demonstrates INT253 CO4 & CO5.
    """
    solution = get_object_or_404(Solution, pk=solution_id)
    challenge = solution.challenge

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.challenge = challenge
            project.solution = solution
            project.lead = request.user
            project.save()

            # Automatically add creator as Project Lead in memberships
            ProjectMembership.objects.create(
                project=project,
                user=request.user,
                role='Project Lead'
            )

            # Update challenge status to in_progress if not already
            if challenge.status in ['pending', 'approved']:
                challenge.status = 'in_progress'
                challenge.save()

            log_activity(
                user=request.user,
                activity_type='project_created',
                title=f"Launched collaborative project: {project.title}",
                link=f"/collaborations/{project.pk}/"
            )

            messages.success(request, f"Collaborative Project '{project.title}' initialized successfully! Invite team members to collaborate.")
            return redirect('collaborations:detail', pk=project.pk)
    else:
        # Pre-fill title and description from solution
        initial_data = {
            'title': f"Project: {solution.title}",
            'description': f"Implementation of solution '{solution.title}' for challenge '{challenge.title}'.\n\nObjective:\n{solution.expected_outcome}",
            'status': 'planning',
            'progress_percentage': 5,
        }
        form = ProjectForm(initial=initial_data)

    return render(request, 'collaborations/project_form.html', {
        'form': form,
        'solution': solution,
        'challenge': challenge,
        'action_title': f"Launch Project for: {solution.title}",
        'is_edit': False
    })


@login_required
def project_create_from_challenge_view(request, challenge_id):
    """
    Initiate a collaborative project directly from an approved challenge.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.challenge = challenge
            project.lead = request.user
            project.save()

            ProjectMembership.objects.create(
                project=project,
                user=request.user,
                role='Project Lead'
            )

            if challenge.status in ['pending', 'approved']:
                challenge.status = 'in_progress'
                challenge.save()

            log_activity(
                user=request.user,
                activity_type='project_created',
                title=f"Initiated project: {project.title}",
                link=f"/collaborations/{project.pk}/"
            )

            messages.success(request, f"Project '{project.title}' launched successfully!")
            return redirect('collaborations:detail', pk=project.pk)
    else:
        initial_data = {
            'title': f"Initiative: {challenge.title}",
            'description': f"Collaborative initiative addressing '{challenge.title}'.\n\nImpact Focus:\n{challenge.expected_impact}",
            'status': 'planning',
            'progress_percentage': 0,
        }
        form = ProjectForm(initial=initial_data)

    return render(request, 'collaborations/project_form.html', {
        'form': form,
        'challenge': challenge,
        'action_title': f"Create Collaboration for: {challenge.title}",
        'is_edit': False
    })


@login_required
def project_edit_view(request, pk):
    """
    Update project milestones, progress percentage, and status.
    """
    project = get_object_or_404(Project, pk=pk)

    if not (request.user == project.lead or request.user.is_admin_user):
        messages.error(request, "Only the project lead or administrator can edit this project.")
        return redirect('collaborations:detail', pk=project.pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            p = form.save()
            # If marked completed, optionally mark challenge as solved
            if p.status == 'completed' and p.progress_percentage == 100:
                p.challenge.status = 'solved'
                p.challenge.save()

            log_activity(
                user=request.user,
                activity_type='project_updated',
                title=f"Updated progress for: {project.title} ({project.progress_percentage}%)",
                link=f"/collaborations/{project.pk}/"
            )
            messages.success(request, "Project progress and details updated successfully.")
            return redirect('collaborations:detail', pk=project.pk)
        else:
            messages.error(request, "Please rectify errors in the project form.")
    else:
        form = ProjectForm(instance=project)

    return render(request, 'collaborations/project_form.html', {
        'form': form,
        'project': project,
        'challenge': project.challenge,
        'action_title': f"Update Project: {project.title}",
        'is_edit': True
    })


@login_required
def project_member_add_view(request, pk):
    """
    Add a team member with designated role to the project.
    """
    project = get_object_or_404(Project, pk=pk)

    if not (request.user == project.lead or request.user.is_admin_user):
        messages.error(request, "Only project leads can add team members.")
        return redirect('collaborations:detail', pk=project.pk)

    if request.method == 'POST':
        form = ProjectMembershipAddForm(request.POST, project=project)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.project = project
            membership.save()

            log_activity(
                user=membership.user,
                activity_type='added_to_project',
                title=f"Added to project team: {project.title} as {membership.role}",
                link=f"/collaborations/{project.pk}/"
            )

            messages.success(request, f"Added {membership.user.display_name} as {membership.role} to the project team.")
        else:
            messages.error(request, "Could not add user. Please select a valid user.")

    return redirect('collaborations:detail', pk=project.pk)


@login_required
def project_member_remove_view(request, pk, membership_id):
    """
    Remove a team member from the project.
    """
    project = get_object_or_404(Project, pk=pk)
    membership = get_object_or_404(ProjectMembership, pk=membership_id, project=project)

    if not (request.user == project.lead or request.user.is_admin_user or request.user == membership.user):
        messages.error(request, "You do not have permission to remove this member.")
        return redirect('collaborations:detail', pk=project.pk)

    if request.method == 'POST':
        username = membership.user.username
        membership.delete()
        messages.info(request, f"Member @{username} has been removed from this project.")

    return redirect('collaborations:detail', pk=project.pk)


@login_required
def project_quick_join_view(request, pk):
    """
    Allow students or citizens to quickly join a project as a Contributor.
    """
    project = get_object_or_404(Project, pk=pk)

    if project.is_member(request.user):
        messages.info(request, "You are already a member of this project team.")
        return redirect('collaborations:detail', pk=project.pk)

    role_title = 'Student Developer' if request.user.is_student else ('Faculty Mentor' if request.user.is_university else 'Contributor')
    ProjectMembership.objects.create(
        project=project,
        user=request.user,
        role=role_title
    )

    log_activity(
        user=request.user,
        activity_type='joined_project',
        title=f"Joined project '{project.title}' as {role_title}",
        link=f"/collaborations/{project.pk}/"
    )

    messages.success(request, f"You have joined '{project.title}' as a {role_title}! Welcome to the team.")
    return redirect('collaborations:detail', pk=project.pk)
