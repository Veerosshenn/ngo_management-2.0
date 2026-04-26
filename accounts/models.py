from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('employee', 'Employee'),
    )
    # Match initial migration: role field with max_length=10
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    # Convenience helpers used in middleware/templates
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_employee(self) -> bool:
        return self.role == 'employee'
