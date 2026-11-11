from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import PartnershipRequest
from .forms import PartnershipRequestForm, PartnershipResponseForm
from collaborations.models import Project
from challenges.models import Challenge
from accounts.utils import log_activity

User = get_user_model()


def partner_directory_view(request):
    """
    Directory of registered Academic Institutions & Industry Leaders.
    Demonstrates INT253 CO2 and CO5.
    """
    role_filter = request.GET.get('role', '').strip()
    q = request.GET.get('q', '').strip()

    partners = User.objects.filter(role__in=['university', 'industry']).order_by('role', 'institution_name')

    if role_filter in ['university', 'industry']:
        partners = partners.filter(role=role_filter)

    if q:
        partners = partners.filter(
            Q(institution_name__icontains=q) |
            Q(username__icontains=q) |
            Q(location__icontains=q) |
            Q(bio__icontains=q)
        )

    context = {
        'partners': partners,
        'role_filter': role_filter,
        'search_query': q,
        'total_universities': User.objects.filter(role='university').count(),
        'total_industries': User.objects.filter(role='industry').count(),
    }
    return render(request, 'partnerships/partner_directory.html', context)


@login_required
def partnership_request_create_view(request):
    """
    Initiate a formal collaboration or mentorship request.
    Demonstrates INT253 CO4 & CO5.
    """
    target_id = request.GET.get('target')
    project_id = request.GET.get('project')
    challenge_id = request.GET.get('challenge')

    initial_data = {}
    if target_id:
        target_user = get_object_or_404(User, pk=target_id)
        initial_data['target_organization'] = target_user
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        initial_data['project'] = project
    if challenge_id:
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        initial_data['challenge'] = challenge

    if request.method == 'POST':
        form = PartnershipRequestForm(request.POST, user=request.user)
        if form.is_valid():
            req = form.save(commit=False)
            req.requesting_organization = request.user
            req.save()

            log_activity(
                user=request.user,
                activity_type='partnership_sent',
                title=f"Sent partnership request to {req.target_organization.display_name}",
                link='/partnerships/'
            )
            log_activity(
                user=req.target_organization,
                activity_type='partnership_received',
                title=f"Received partnership proposal from {request.user.display_name}",
                link='/partnerships/'
            )

            messages.success(request, f"Partnership request sent to {req.target_organization.display_name} successfully!")
            return redirect('partnerships:list')
        else:
            messages.error(request, "Please check the form inputs and try again.")
    else:
        form = PartnershipRequestForm(initial=initial_data, user=request.user)

    return render(request, 'partnerships/partnership_request_form.html', {
        'form': form,
    })


@login_required
def partnership_list_view(request):
    """
    View all incoming and outgoing partnership proposals.
    """
    user = request.user
    received_requests = PartnershipRequest.objects.filter(
        target_organization=user
    ).select_related('requesting_organization', 'project', 'challenge')

    sent_requests = PartnershipRequest.objects.filter(
        requesting_organization=user
    ).select_related('target_organization', 'project', 'challenge')

    pending_count = received_requests.filter(status='pending').count()

    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'pending_count': pending_count,
    }
    return render(request, 'partnerships/partnership_list.html', context)


@login_required
def partnership_respond_view(request, pk):
    """
    Accept or decline an incoming partnership request with remarks.
    """
    req = get_object_or_404(PartnershipRequest, pk=pk, target_organization=request.user)

    if request.method == 'POST':
        form = PartnershipResponseForm(request.POST, instance=req)
        if form.is_valid():
            p_req = form.save()

            status_text = 'Accepted' if p_req.status == 'accepted' else 'Declined'
            log_activity(
                user=p_req.requesting_organization,
                activity_type='partnership_responded',
                title=f"{request.user.display_name} has {status_text.lower()} your partnership request.",
                link='/partnerships/'
            )

            messages.success(request, f"Partnership request status marked as: {status_text}.")
            return redirect('partnerships:list')
    else:
        form = PartnershipResponseForm(instance=req)

    return render(request, 'partnerships/partnership_respond.html', {
        'form': form,
        'partnership': req,
    })
