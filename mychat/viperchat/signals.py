from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.models import Permission

from .models import UserPermissionSettings, ServerInvite, Notification


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_permission_settings(sender, instance, created, *args, **kwargs):
    """
    Creates UserPermissionSettings model instance
    """
    if created:
        UserPermissionSettings.objects.create(user=instance)
        

@receiver(post_save, sender=ServerInvite)
def create_invite_notification(sender, instance, created, *args, **kwargs):
    """
    Creates notification after room invite send
    """
    pass