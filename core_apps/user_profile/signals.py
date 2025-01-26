from typing import Any
from django.db.models.base import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from loguru import logger
from django.conf import settings

from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender: type[Model], instance: Model, created: bool, **kwargs: Any) -> None:
    """
    Signal handler to automatically create a Profile when a new User is created.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: Boolean; True if a new record was created
        **kwargs: Additional keyword arguments
    """
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for {instance.first_name} {instance.last_name}")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender: type[Model], instance: Model, **kwargs: Any) -> None:
    """
    Signal handler to save Profile when User is updated.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    instance.profile.save()