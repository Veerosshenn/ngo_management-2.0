from django.db import models
from django.conf import settings
from django.utils import timezone


class NGO(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'NGO'
        verbose_name_plural = 'NGOs'
        ordering = ['name']

    def __str__(self):
        return self.name


class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    date = models.DateTimeField()
    cut_off_datetime = models.DateTimeField(help_text='Registration deadline')
    max_slots = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='created_activities'
    )
    ngo = models.ForeignKey(
        'ngo.NGO',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activities'
    )

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['date']

    def __str__(self):
        return self.title

    def is_registration_open(self):
        """Check if registration is still open based on cut-off datetime."""
        return timezone.now() <= self.cut_off_datetime

    def slots_remaining(self):
        """Return number of available slots."""
        return self.max_slots - self.registrations.filter(status='active').count()

    def has_slots_available(self):
        """Check if there are still slots available."""
        return self.slots_remaining() > 0

    def get_registered_count(self):
        """Return number of active registrations."""
        return self.registrations.filter(status='active').count()
