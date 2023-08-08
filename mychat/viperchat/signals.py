from django.db.models.signals import post_save, pre_delete, post_delete
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user

from .models import UserPermissionSettings, ServerInvite, Notification


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_permission_settings_post_save(sender, instance, created, *args, **kwargs):
    """
    Creates UserPermissionSettings model instance
    """
    if created:
        UserPermissionSettings.objects.create(user=instance)
        

@receiver(post_save, sender=ServerInvite)
def create_invite_notification_post_save(sender, instance, created, *args, **kwargs):
    """
    Creates notification after room invite send
    """
    if created:
        description = f'{instance.invitation_sender} sent you invite to {instance.server} server.'
        Notification.objects.create(description=description, receiver=instance.receiver)


@receiver(post_delete, sender=ServerInvite)
def create_server_invite_answer_notifaction_post_delete(sender, instance, *args, **kwargs):
    """
    Creates notification depends on ServerInvite status field 
    """
    if instance.status == 'accepted':
        description = f'{instance.receiver} has accepted your invite to {instance.server} server'
        Notification.objects.create(description=description, receiver=instance.invitation_sender)
    elif instance.status == 'declined':
        description = f'{instance.receiver} has declined your invite to {instance.server} server'
        Notification.objects.create(description=description, receiver=instance.invitation_sender)