"""
accounts/signals.py

Topic 6.1 – User Accounts and Roles / Groups
----------------------------------------------
Whenever a CustomUser is saved, this signal handler ensures they belong to
the correct Django Group ('Administrators' or 'Employees').  Groups carry
model-level permissions that Django's built-in permission system can check
via request.user.has_perm(…).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db import DatabaseError


@receiver(post_save, sender='accounts.CustomUser')
def assign_user_group(sender, instance, created, **kwargs):
    """
    Auto-assign the user to the matching Django Group based on their role.
    Creates the group on first use if it does not yet exist.
    """
    group_name = 'Administrators' if instance.is_admin() else 'Employees'
    group, _ = Group.objects.get_or_create(name=group_name)

    # Remove from the opposite group so a role change is reflected immediately
    other = 'Employees' if instance.is_admin() else 'Administrators'
    other_group = Group.objects.filter(name=other).first()
    if other_group:
        instance.groups.remove(other_group)

    instance.groups.add(group)
