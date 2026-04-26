from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Activity, NGO
from .forms import ActivityForm


def activity_list(request):
    activities = Activity.objects.annotate(
        registered_count=Count(
            'registrations',
            filter=Q(registrations__status='active')
        )
    )
    return render(request, 'ngo/activity_list.html', {
        'activities': activities
    })


def activity_detail(request, activity_id):
    from registration.models import Registration
    
    activity = get_object_or_404(Activity, id=activity_id)
    registered_count = activity.registrations.filter(status='active').count()
    is_registered = request.user.is_authenticated and Registration.objects.filter(
        employee=request.user,
        activity=activity,
        status='active'
    ).exists()
    
    return render(request, 'ngo/activity_detail.html', {
        'activity': activity,
        'registered_count': registered_count,
        'is_registered': is_registered,
    })


@login_required
def activity_create(request):
    """Create a new activity (admin only)."""
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'You do not have permission to create activities.')
        return redirect('ngo:activity_list')
    
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            messages.success(request, f'Activity "{activity.title}" created successfully.')
            return redirect('ngo:activity_detail', activity_id=activity.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ActivityForm()
    
    return render(request, 'ngo/activity_form.html', {'form': form, 'title': 'Create Activity'})


@login_required
def activity_edit(request, activity_id):
    """Edit an existing activity (admin only)."""
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'You do not have permission to edit activities.')
        return redirect('ngo:activity_list')
    
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, f'Activity "{activity.title}" updated successfully.')
            return redirect('ngo:activity_detail', activity_id=activity.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ActivityForm(instance=activity)
    
    return render(request, 'ngo/activity_form.html', {'form': form, 'activity': activity, 'title': 'Edit Activity'})


@login_required
def activity_delete(request, activity_id):
    """Delete an activity (admin only)."""
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'You do not have permission to delete activities.')
        return redirect('ngo:activity_list')
    
    activity = get_object_or_404(Activity, id=activity_id)
    
    if request.method == 'POST':
        activity_title = activity.title
        activity.delete()
        messages.success(request, f'Activity "{activity_title}" deleted.')
        return redirect('ngo:activity_list')
    
    return render(request, 'ngo/activity_confirm_delete.html', {'activity': activity})