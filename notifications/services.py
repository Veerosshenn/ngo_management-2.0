from notifications.models import Notification
from notifications.tasks import send_email_notification_task


def send_notification(user, message):
    """
    Creates a Notification record for the given user.
    This is the central notification service used by other apps.
    """
    n = Notification.objects.create(recipient=user, message=message)
    # Topic 10: send email in background (queue/worker)
    send_email_notification_task.delay(n.id)
    return n
