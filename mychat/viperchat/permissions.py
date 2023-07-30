from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from .models import Message, Room, RoomInvite

User = get_user_model()

"""-------------------------------------GROUP PERMISSIONS----------------------------"""

def delete_delete_message_permission(group):
    message_content_type = ContentType.objects.get_for_model(Message)
    permission = Permission.objects.get(codename='delete_message_from_room', content_type=message_content_type)
    if permission:
        return group.permissions.filter(codename='delete_message_from_room', content_type=message_content_type).first().delete()


def add_delete_message_permission(group):
    message_content_type = ContentType.objects.get_for_model(Message)
    permission = Permission.objects.get(codename='delete_message_from_room', content_type=message_content_type)
    group.permissions.add(permission)
    return group.save()


def delete_user_from_group_permission(group):
    room_content_type = ContentType.objects.get_for_model(Room)
    return group.permissions.get(codename='delete_user_from_room', content_type=room_content_type).delete()


def add_delete_user_from_group_permission(group):
    room_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='delete_user_from_room', content_type=room_content_type)
    return group.permissions.add(permission)


def delete_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(RoomInvite)
    return group.permissions.filter(codename='send_invitation', content_type=send_invite_content_type).first().delete()


def add_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(RoomInvite)
    permission = Permission.objects.get(codename='send_invitation', content_type=send_invite_content_type)
    group.permissions.add(permission)
    return group.save()


def delete_display_room_data_permission(group):
    display_room_data_content_type = ContentType.objects.get_for_model(Room)
    return group.permissions.get(codename='display_room_data', content_type=display_room_data_content_type).delete()


def add_display_room_data_permission(group):
    display_room_data_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='display_room_data', content_type=display_room_data_content_type)
    return group.permissions.add(permission)


def delete_display_user_profile_permission(group):
    display_user_data_content_type = ContentType.objects.get_for_model(User)
    return group.permissions.get(codename='display_user_profile', content_type=display_user_data_content_type).delete()


def add_display_user_profile_permission(group):
    display_user_data_content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='display_user_profile', content_type=display_user_data_content_type)
    return group.permissions.add(permission)

"""-----------------------------------------------------------------------------------"""

def set_permission(permission, group, action_true, action_false):
    if permission == 'Allowed':
        action_true(group)
    elif permission == 'Forbidden':
        action_false(group)