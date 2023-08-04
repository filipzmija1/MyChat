from django.contrib.auth.models import Group, Permission
from django.forms.models import model_to_dict
from django.urls import reverse
from django.shortcuts import redirect

from .models import Server
from .permissions import *


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
    add_edit_permissions_in_server(owners)
    add_delete_user_from_server_permission(owners)
    #   Masters permissions
    add_delete_message_permission(masters)
    add_send_invitation_permission(masters)
    add_send_messages_in_server_permission(masters)
    add_delete_moderators_from_server_permission(masters)
    add_delete_members_from_server_permission(masters)
    add_delete_user_from_server_permission(masters)
    #   Moderators permissions
    add_delete_message_permission(moderators)
    add_send_invitation_permission(moderators)
    add_send_messages_in_server_permission(moderators)
    add_delete_members_from_server_permission(moderators)
    add_delete_user_from_server_permission(moderators)
    #   Members permissions
    add_send_messages_in_server_permission(members)
    add_send_invitation_permission(members)


def check_if_logged_user_can_delete_user(logged_user, user_to_delete, server):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    permission_settings = server.permission_settings
    owners_group = Group.objects.get(name=f'{server.name}_owners')
    masters_group = Group.objects.get(name=f'{server.name}_masters')
    members_group = Group.objects.get(name=f'{server.name}_members')

    owners_delete_permissions = [
        Permission.objects.get(codename='delete_masters_from_server'),
        Permission.objects.get(codename='delete_moderators_from_server'),
        Permission.objects.get(codename='delete_members_from_server')
    ]

    masters_delete_permissions = [
        Permission.objects.get(codename='delete_moderators_from_server'),
        Permission.objects.get(codename='delete_members_from_server')
    ]

    moderator_delete_permissions = [
        Permission.objects.get(codename='delete_members_from_server')
    ]
    
    for group in server_groups:
        if user_to_delete in owners_group.user_set.all():
            return False
        #   Owners group
        if logged_user in group.user_set.all() and \
        all(permission in group.permissions.all() for permission in owners_delete_permissions): 
            if user_to_delete in owners_group.user_set.all():   #   Delete owners is prohibited
                return False
            else:
                return True
        #   Masters group
        if logged_user in group.user_set.all() and \
        all(permission in group.permissions.all() for permission in masters_delete_permissions): 
            #   Check if masters have permission to delete user
            if permission_settings.masters_delete_user == 'Forbidden' and \
            user_to_delete in owners_group.user_set.all() or \
            user_to_delete in masters_group.user_set.all():
                return False
            else:
                return True
        #   Moderators group
        if logged_user in group.user_set.all()  \
        and all(permission in group.permissions.all() for permission in moderator_delete_permissions):
            #   Check if moderators have permission to delete user
            if user_to_delete in members_group.user_set.all() and permission_settings.moderators_delete_user == 'Allowed':
                return True
            else:
                return False
            

def set_masters_permissions(server_model_instance):
    permission_settings = server_model_instance.permission_settings
    masters_group = Group.objects.get(name=f'{server_model_instance.name}_masters')
    #   masters permission settings
    masters_settings = {permission: value for permission, value in model_to_dict(permission_settings).items() 
                        if permission.startswith('masters_')}
    
    #   set masters group permissions
    for permission, value in masters_settings.items():
        if permission == 'masters_create_room':
            set_permission(value, masters_group, add_create_room_in_server_permission, remove_create_room_in_server_permission)
        if permission == 'masters_send_invitation_to_group':
            set_permission(value, masters_group, add_send_invitation_permission, remove_send_invitation_permission)
        if permission == 'masters_delete_user':
            set_permission(value, masters_group, add_delete_user_from_server_permission, remove_delete_user_from_server_permission)
            set_permission(value, masters_group, add_delete_moderators_from_server_permission, remove_delete_moderators_from_server_permission)
            set_permission(value, masters_group, add_delete_members_from_server_permission, remove_delete_members_from_server_permission)
        if permission == 'masters_delete_messages':
            set_permission(value, masters_group, add_delete_message_permission, remove_delete_message_permission)
        if permission == 'masters_send_messages':
            set_permission(value, masters_group, add_send_messages_in_server_permission, remove_send_messages_in_server_permission)
        if permission == 'masters_can_see_private_rooms':
            set_permission(value, masters_group, add_display_room_data_permission, remove_display_room_data_permission)
    masters_group.save()
    return "Permissions changed successfully"


def set_moderators_permissions(server_model_instance):
    permission_settings = server_model_instance.permission_settings
    moderators_group = Group.objects.get(name=f'{server_model_instance.name}_moderators')
    #   moderator permission settings
    moderators_settings = {permission: value for permission, value in model_to_dict(permission_settings).items() 
                        if permission.startswith('moderators_')}
    #   set moderators group permissions
    for permission, value in moderators_settings.items():
        if permission == 'moderators_create_room':
            set_permission(value, moderators_group, add_create_room_in_server_permission, remove_create_room_in_server_permission)
        if permission == 'moderators_send_invitation_to_group':
            set_permission(value, moderators_group, add_send_invitation_permission, remove_send_invitation_permission)
        if permission == 'moderators_delete_user':
            set_permission(value, moderators_group, add_delete_user_from_server_permission, remove_delete_user_from_server_permission)
            set_permission(value, moderators_group, add_delete_members_from_server_permission, remove_delete_members_from_server_permission)
        if permission == 'moderators_delete_messages':
            set_permission(value, moderators_group, add_delete_message_permission, remove_delete_message_permission)
        if permission == 'moderators_send_messages':
            set_permission(value, moderators_group, add_send_messages_in_server_permission, remove_send_messages_in_server_permission)
        if permission == 'moderators_can_see_private_rooms':
            set_permission(value, moderators_group, add_display_room_data_permission, remove_display_room_data_permission)
    moderators_group.save()
    return "Permissions changed successfully"


def set_members_permissions(server_model_instance):
    members_group = Group.objects.get(name=f'{server_model_instance.name}_members')
    permission_settings = server_model_instance.permission_settings
     #   members permission settings
    members_settings = {permission: value for permission, value in model_to_dict(permission_settings).items()
                        if permission.startswith('members_')}
    # #   set members group permissions
    for permission, value in members_settings.items():
        if permission == 'members_create_room':
            set_permission(value, members_group, add_create_room_in_server_permission, remove_create_room_in_server_permission)
        if permission == 'members_send_invitation_to_group':
            set_permission(value, members_group, add_send_invitation_permission, remove_send_invitation_permission)
        if permission == 'members_delete_messages':
            set_permission(value, members_group, add_delete_message_permission, remove_delete_message_permission)
        if permission == 'members_send_messages':
            set_permission(value, members_group, add_send_messages_in_server_permission, remove_send_messages_in_server_permission)
        if permission == 'members_can_see_private_rooms':
            set_permission(value, members_group, add_display_room_data_permission, remove_display_room_data_permission)
    members_group.save()
    return "Permissions changed successfully"
    

def set_permission(permission_settings_model_value, group, add_permission_function, remove_permission_function):
    if permission_settings_model_value == 'Allowed':
        add_permission_function(group)
        group.save()
    elif permission_settings_model_value == 'Forbidden':
        remove_permission_function(group)
        group.save()
