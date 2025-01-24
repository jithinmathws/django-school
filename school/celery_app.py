import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school.settings.local")

# Create the Celery application instance
app = Celery("outshine_international_school")

# Load task configuration values from the Django settings object
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    """Task for debugging purposes"""
    print(f'Request: {self.request!r}')