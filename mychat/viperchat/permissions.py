from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from .models import Message, Room, RoomInvite, Server

User = get_user_model()

"""-------------------------------------GROUP PERMISSIONS----------------------------"""

def remove_delete_message_permission(group):
    message_content_type = ContentType.objects.get_for_model(Message)
    permission = Permission.objects.get(codename='delete_message_from_server', content_type=message_content_type)
    return group.permissions.remove(permission)


def add_delete_message_permission(group):
    message_content_type = ContentType.objects.get_for_model(Message)
    permission = Permission.objects.get(codename='delete_message_from_server', content_type=message_content_type)
    group.permissions.add(permission)
    return group.save()


def remove_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(RoomInvite)
    permission = Permission.objects.get(codename='send_invitation', content_type=send_invite_content_type)
    return group.permissions.remove(permission)


def add_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(RoomInvite)
    permission = Permission.objects.get(codename='send_invitation', content_type=send_invite_content_type)
    group.permissions.add(permission)
    return group.save()


def remove_display_room_data_permission(group):
    display_room_data_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='display_room_data', content_type=display_room_data_content_type)
    return group.permissions.remove(permission)


def add_display_room_data_permission(group):
    display_room_data_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='display_room_data', content_type=display_room_data_content_type)
    return group.permissions.add(permission)


def remove_display_user_profile_permission(group):
    display_user_data_content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='display_user_profile', content_type=display_user_data_content_type)
    return group.permissions.remove(permission)


def add_display_user_profile_permission(group):
    display_user_data_content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='display_user_profile', content_type=display_user_data_content_type)
    return group.permissions.add(permission)


def add_create_room_in_server_permission(group):
    create_room_in_server_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='create_room_in_server', content_type=create_room_in_server_content_type)
    return group.permissions.add(permission)


def remove_create_room_in_server_permission(group):
    create_room_in_server_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='create_room_in_server', content_type=create_room_in_server_content_type)
    return group.permissions.remove(permission)


def add_send_messages_in_server_permission(group):
    send_messages_in_server_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='send_messages_in_server', content_type=send_messages_in_server_content_type)
    return group.permissions.add(permission)


def remove_send_messages_in_server_permission(group):
    send_messages_in_server_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='send_messages_in_server', content_type=send_messages_in_server_content_type)
    return group.permissions.remove(permission)


def add_delete_masters_from_server_permission(group):
    delete_masters_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='delete_masters_from_server', content_type=delete_masters_content_type)
    return group.permissions.add(permission)

def remove_delete_masters_from_server_permission(group):
    delete_masters_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='delete_masters_from_server', content_type=delete_masters_content_type)
    return group.permissions.remove(permission)


def add_delete_moderators_from_server_permission(group):
    delete_moderators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='delete_moderators_from_server', content_type=delete_moderators_content_type)
    return group.permissions.add(permission)

def remove_delete_moderators_from_server_permission(group):
    delete_moderators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='delete_moderators_from_server', content_type=delete_moderators_content_type)
    return group.permissions.remove(permission)


def add_delete_members_from_server_permission(group):
    delete_members_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='delete_members_from_server', content_type=delete_members_content_type)
    return group.permissions.add(permission)


def remove_delete_members_from_server_permission(group):
    delete_members_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='delete_members_from_server', content_type=delete_members_content_type)
    return group.permissions.remove(permission)

"""-----------------------------------------------------------------------------------"""

def set_permission(permission, group, action_true, action_false):
    if permission == 'Allowed':
        action_true(group)
        group.save()
    elif permission == 'Forbidden':
        action_false(group)
        group.save()


def initial_server_permissions(owners, masters, moderators, members):
    """Set initial permissions for groups in server"""
    #   Owners permissions
    add_delete_message_permission(owners)
    add_send_invitation_permission(owners)
    add_create_room_in_server_permission(owners)
    add_send_messages_in_server_permission(owners)
    add_delete_masters_from_server_permission(owners)
    add_delete_moderators_from_server_permission(owners)
    add_delete_members_from_server_permission(owners)
    #   Masters permissions
    add_delete_message_permission(masters)
    add_send_invitation_permission(masters)
    add_send_messages_in_server_permission(masters)
    add_delete_moderators_from_server_permission(masters)
    add_delete_members_from_server_permission(masters)
    #   Moderators permissions
    add_delete_message_permission(moderators)
    add_send_invitation_permission(moderators)
    add_send_messages_in_server_permission(moderators)
    add_delete_members_from_server_permission(moderators)
    #   Members permissions
    add_send_messages_in_server_permission(members)
    add_send_invitation_permission(members)



