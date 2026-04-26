from django.db import models
from django.conf import settings


class Registration(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    activity = models.ForeignKey(
        'ngo.Activity',
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('cancelled', 'Cancelled')],
        default='active'
    )
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkins_recorded',
    )

    class Meta:
        ordering = ['-registered_at']
        unique_together = [('employee', 'activity')]

    def __str__(self):
        return f"{self.employee.username} - {self.activity.title}"
