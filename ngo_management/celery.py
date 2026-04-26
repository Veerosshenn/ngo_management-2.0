import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ngo_management.settings")

app = Celery("ngo_management")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

