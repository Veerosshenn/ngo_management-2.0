"""
registration/services.py

Topic 4.5 – Transactions and Locking
--------------------------------------
All slot-availability checks and row inserts happen inside a single
atomic transaction. The Activity row is locked with SELECT FOR UPDATE so
that two concurrent requests cannot both read "1 slot left" and both
succeed – only the first commit wins; the second sees 0 and is rejected.
"""

from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import Registration


class RegistrationService:

    @staticmethod
    @transaction.atomic                     # Topic 4.5 – atomic block
    def register_user(user, activity_id):
        """
        Register *user* for the activity identified by *activity_id*.

        Raises ValueError for business-rule violations so the caller can
        surface a friendly message without crashing.
        """
        from ngo.models import Activity

    
        activity = (
            Activity.objects
            .select_for_update()            #lock activity row, prevents concurrent updates
            .get(id=activity_id)
        )

        # Topic 5.3 – validation at service layer
        if not activity.is_registration_open():   # check if registration is still open
            raise ValueError(
                "Registration is closed – the cut-off date has passed."
            )

       #are slots available? Count active registrations for this activity and compare to max_slots
        registered = activity.registrations.filter(status='active').count()
        if registered >= activity.max_slots:
            raise ValueError(
                "Sorry, this activity is fully booked. No slots remaining."
            )

        # ── Create or reactivate the registration ────────────────────────────
        try:
            registration, created = Registration.objects.get_or_create(
                employee=user,
                activity=activity,
                defaults={'status': 'active'},
            )
        except IntegrityError:
            # Concurrent transaction already inserted the same pair.
            raise ValueError("You are already registered for this activity.")

        if not created:
            if registration.status == 'cancelled':
                registration.status = 'active'
                registration.registered_at = timezone.now()
                registration.save(update_fields=['status', 'registered_at'])
            else:
                raise ValueError("You are already registered for this activity.")

        return registration