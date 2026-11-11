from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Solution
from .forms import SolutionForm
from challenges.models import Challenge
from accounts.utils import log_activity


@login_required
def solution_create_view(request, challenge_id):
    """
    Submit an innovative proposed solution to an approved challenge.
    Demonstrates INT253 CO4 & CO5.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # Only approved challenges can accept solutions
    if challenge.status not in ['approved', 'in_progress']:
        messages.warning(request, "Solutions can only be submitted for approved challenges.")
        return redirect('challenges:detail', pk=challenge.pk)

    if request.method == 'POST':
        form = SolutionForm(request.POST)
        if form.is_valid():
            solution = form.save(commit=False)
            solution.challenge = challenge
            solution.creator = request.user
            solution.save()

            log_activity(
                user=request.user,
                activity_type='solution_submitted',
                title=f"Submitted solution '{solution.title}' for '{challenge.title}'",
                link=f"/solutions/{solution.pk}/"
            )

            messages.success(request, f"Your solution '{solution.title}' was submitted successfully!")
            return redirect('solutions:detail', pk=solution.pk)
        else:
            messages.error(request, "Please correct the errors in the solution form.")
    else:
        form = SolutionForm()

    return render(request, 'solutions/solution_form.html', {
        'form': form,
        'challenge': challenge,
        'action_title': f"Submit Solution for: {challenge.title}",
        'is_edit': False
    })


def solution_detail_view(request, pk):
    """
    View solution details, technical specifications, and related collaborative project.
    """
    solution = get_object_or_404(Solution.objects.select_related('challenge', 'creator'), pk=pk)
    challenge = solution.challenge

    is_creator = (request.user.is_authenticated and request.user == solution.creator)
    is_challenge_owner = (request.user.is_authenticated and request.user == challenge.creator)
    can_manage = is_creator or (request.user.is_authenticated and request.user.is_admin_user)
    can_accept = is_challenge_owner or (request.user.is_authenticated and request.user.is_admin_user)

    return render(request, 'solutions/solution_detail.html', {
        'solution': solution,
        'challenge': challenge,
        'is_creator': is_creator,
        'is_challenge_owner': is_challenge_owner,
        'can_manage': can_manage,
        'can_accept': can_accept,
    })


@login_required
def solution_edit_view(request, pk):
    """
    Edit an existing solution (restricted to solution creator or admin).
    """
    solution = get_object_or_404(Solution, pk=pk)

    if not (request.user == solution.creator or request.user.is_admin_user):
        messages.error(request, "You are not authorized to edit this solution.")
        return redirect('solutions:detail', pk=solution.pk)

    if request.method == 'POST':
        form = SolutionForm(request.POST, instance=solution)
        if form.is_valid():
            form.save()
            log_activity(
                user=request.user,
                activity_type='solution_updated',
                title=f"Updated solution: {solution.title}",
                link=f"/solutions/{solution.pk}/"
            )
            messages.success(request, "Solution details updated successfully.")
            return redirect('solutions:detail', pk=solution.pk)
        else:
            messages.error(request, "Please rectify errors indicated below.")
    else:
        form = SolutionForm(instance=solution)

    return render(request, 'solutions/solution_form.html', {
        'form': form,
        'solution': solution,
        'challenge': solution.challenge,
        'action_title': f"Edit Solution: {solution.title}",
        'is_edit': True
    })


@login_required
def solution_delete_view(request, pk):
    """
    Delete a proposed solution (restricted to author or admin).
    """
    solution = get_object_or_404(Solution, pk=pk)
    challenge_pk = solution.challenge.pk

    if not (request.user == solution.creator or request.user.is_admin_user):
        messages.error(request, "You do not have permission to delete this solution.")
        return redirect('solutions:detail', pk=solution.pk)

    if request.method == 'POST':
        title = solution.title
        solution.delete()
        log_activity(
            user=request.user,
            activity_type='solution_deleted',
            title=f"Deleted solution: {title}"
        )
        messages.success(request, f"Solution '{title}' has been deleted.")
        return redirect('challenges:detail', pk=challenge_pk)

    return render(request, 'solutions/solution_confirm_delete.html', {'solution': solution})


@login_required
def solution_accept_toggle_view(request, pk):
    """
    Mark a solution as accepted or revoke acceptance.
    Accessible to Challenge creator or Admin.
    """
    solution = get_object_or_404(Solution, pk=pk)
    challenge = solution.challenge

    if not (request.user == challenge.creator or request.user.is_admin_user):
        messages.error(request, "Only the challenge owner or an administrator can accept solutions.")
        return redirect('solutions:detail', pk=solution.pk)

    if request.method == 'POST':
        if solution.is_accepted:
            solution.is_accepted = False
            solution.save()
            messages.info(request, f"Solution '{solution.title}' is no longer marked as accepted.")
        else:
            # Set this solution to accepted
            solution.is_accepted = True
            solution.save()

            # Optionally update challenge status to in_progress if still approved
            if challenge.status == 'approved':
                challenge.status = 'in_progress'
                challenge.save()

            log_activity(
                user=solution.creator,
                activity_type='solution_accepted',
                title=f"Your solution '{solution.title}' was accepted by {challenge.creator.display_name}!",
                link=f"/solutions/{solution.pk}/"
            )
            messages.success(request, f"Solution '{solution.title}' is now accepted! You can now launch a collaborative project.")

    return redirect('solutions:detail', pk=solution.pk)
