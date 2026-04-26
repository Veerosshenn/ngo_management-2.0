from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from notifications.models import Notification


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_email_notification_task(self, notification_id: int):
    """
    Topic 10: Background email sending.
    We create a Notification in DB synchronously, then send email asynchronously.
    """
    notification = Notification.objects.select_related("recipient").get(pk=notification_id)
    user = notification.recipient

    if not user.email:
        return {"status": "skipped", "reason": "no_email"}

    send_mail(
        subject="Service Day Dashboard Notification",
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return {"status": "sent"}


@shared_task
def send_upcoming_activity_reminders():
    """
    Topic 10.2: Scheduled reminder job.
    Sends reminders for activities happening within the next 24 hours
    to employees who are actively registered.
    """
    from ngo.models import Activity
    from registration.models import Registration

    now = timezone.now()
    window_end = now + timezone.timedelta(hours=24)

    upcoming = Activity.objects.filter(date__gte=now, date__lte=window_end)
    sent = 0

    regs = (
        Registration.objects
        .filter(status="active", activity__in=upcoming)
        .select_related("employee", "activity")
    )
    for r in regs:
        msg = f'Reminder: "{r.activity.title}" is happening at {r.activity.date} in {r.activity.location}.'
        n = Notification.objects.create(recipient=r.employee, message=msg)
        send_email_notification_task.delay(n.id)
        sent += 1

    return {"status": "ok", "reminders_sent": sent}

