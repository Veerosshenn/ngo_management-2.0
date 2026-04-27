from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from notifications.models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by("-sent_at")
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def unread_status(request):
    """
    Near real-time notification polling endpoint (Topic 10.3 bonus).
    Returns unread count and newest unread notifications.
    """
    qs = Notification.objects.filter(recipient=request.user, is_read=False).order_by("-sent_at")

    since_id = request.GET.get("since_id")
    if since_id and since_id.isdigit():
        qs = qs.filter(id__gt=int(since_id))

    latest = list(
        qs.values("id", "message", "sent_at")[:5]
    )
    return JsonResponse(
        {
            "unread_count": Notification.objects.filter(recipient=request.user, is_read=False).count(),
            "latest": [
                {
                    "id": n["id"],
                    "message": n["message"],
                    "sent_at": n["sent_at"].isoformat() if n["sent_at"] else None,
                }
                for n in latest
            ],
        }
    )


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
