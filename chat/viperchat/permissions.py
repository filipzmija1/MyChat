from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from .models import Message, Room, ServerInvite, Server

User = get_user_model()

"""-------------------------------------GROUP PERMISSIONS----------------------------"""

def add_only_friends_see_your_profile(group):
    content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='friends_see_profile', content_type=content_type)
    return group.permissions.add(permission)


def remove_only_friends_see_your_profile(group):
    content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='friends_see_profile', content_type=content_type)
    return group.permissions.remove(permission)


def add_edit_rooms_in_server(group):
    edit_rooms_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_rooms_in_server', content_type=edit_rooms_content_type)
    return group.permissions.add(permission)


def remove_edit_rooms_in_server(group):
    edit_rooms_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_rooms_in_server', content_type=edit_rooms_content_type)
    return group.permissions.remove(permission)


def add_edit_moderators_group(group):
    edit_mdoerators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_moderators_group', content_type=edit_mdoerators_content_type)
    return group.permissions.add(permission)


def remove_edit_moderators_group(group):
    edit_mdoerators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_moderators_group', content_type=edit_mdoerators_content_type)
    return group.permissions.remove(permission)


def add_edit_masters_group(group):
    edit_mdoerators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_masters_group', content_type=edit_mdoerators_content_type)
    return group.permissions.add(permission)


def remove_edit_masters_group(group):
    edit_mdoerators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_masters_group', content_type=edit_mdoerators_content_type)
    return group.permissions.remove(permission)


def add_edit_members_group(group):
    edit_mdoerators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_members_group', content_type=edit_mdoerators_content_type)
    return group.permissions.add(permission)


def remove_edit_members_group(group):
    edit_mdoerators_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_members_group', content_type=edit_mdoerators_content_type)
    return group.permissions.remove(permission)


def add_edit_users_group(group):
    edit_user_content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='change_user_group', content_type=edit_user_content_type)
    return group.permissions.add(permission)


def remove_edit_users_group(group):
    edit_user_content_type = ContentType.objects.get_for_model(User)
    permission = Permission.objects.get(codename='change_user_group', content_type=edit_user_content_type)
    return group.permissions.remove(permission)


def add_delete_user_from_server_permission(group):
    delete_user_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='delete_user_from_server', content_type=delete_user_content_type)
    return group.permissions.add(permission)


def remove_delete_user_from_server_permission(group):
    delete_user_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='delete_user_from_server', content_type=delete_user_content_type)
    return group.permissions.remove(permission)


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
    send_invite_content_type = ContentType.objects.get_for_model(ServerInvite)
    permission = Permission.objects.get(codename='send_invitation', content_type=send_invite_content_type)
    return group.permissions.remove(permission)


def add_send_invitation_permission(group):
    send_invite_content_type = ContentType.objects.get_for_model(ServerInvite)
    permission = Permission.objects.get(codename='send_invitation', content_type=send_invite_content_type)
    group.permissions.add(permission)
    return group.save()


def remove_display_room_data_permission(group):
    display_room_data_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='display_private_room_data', content_type=display_room_data_content_type)
    return group.permissions.remove(permission)


def add_display_room_data_permission(group):
    display_room_data_content_type = ContentType.objects.get_for_model(Room)
    permission = Permission.objects.get(codename='display_private_room_data', content_type=display_room_data_content_type)
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


def add_edit_permissions_in_server(group):
    edit_permission_content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='edit_permissions_in_server', content_type=edit_permission_content_type)
    return group.permissions.add(permission)

"""-----------------------------------------------------------------------------------"""




