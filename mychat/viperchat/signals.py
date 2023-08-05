from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from .models import UserPermissionSettings


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_permission_settings(sender, instance, created, **kwargs):
    """Creates UserPermissionSettings model instance"""
    if created:
        UserPermissionSettings.objects.create(user=instance)
        