from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Message, Room, RoomInvite


def delete_delete_message_permission(group):
    message_content_type = ContentType.objects.get_for_model(Message)
    return group.permissions.get(codename='delete_message_from_room', content_type=message_content_type).delete()


def add_delete_message_permission(group):
    message_content_type = ContentType.objects.get_for_model(Message)
    permission = Permission.objects.get(codename='delete_message_from_room', content_type=message_content_type)
    return group.permissions.add(permission)


def delete_user_from_group_permission(group):
    room_content_type = ContentType.objects.get_for_model(Room)
    return group.permissions.get(codename='delete_user_from_room', content_type=room_content_type).delete()


def add_delete_user_message_permission(group):
    room_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='delete_user_from_room', content_type=room_content_type)
    return group.permissions.add(permission)


def delete_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(RoomInvite)
    return group.permissions.get(codename='send_invitation', content_type=send_invite_content_type)


def add_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(RoomInvite)
    permission = Permission.objects.get(odename='send_invitation', content_type=send_invite_content_type)
    return group.permissions.add(permission)