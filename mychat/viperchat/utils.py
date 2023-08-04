from django.contrib.auth.models import Group, Permission
from .models import Server


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
            