from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from notifications.models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
    return JsonResponse({'status': 'ok'})


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
