from django import template
from django.contrib.auth.models import Group, Permission

from viperchat.utils import check_if_logged_user_can_delete_user, check_if_logged_user_can_change_users_group
from viperchat.models import ServerInvite

register = template.Library()

@register.filter
def split_group_name(name):
    return name.split("_")[-1]


@register.filter
def group_users(group):
    return group.user_set.all()


@register.simple_tag
def check_if_logged_user_private_room_permission(logged_user, server):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    user_group = [group for group in server_groups if logged_user in group.user_set.all()]
    permission = Permission.objects.get(codename='display_private_room_data')
    if permission in user_group[0].permissions.all():
        return True
    else:
        return False


@register.simple_tag
def user_group(user, server):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    user_group = [group for group in server_groups if user in group.user_set.all()]
    return user_group[0].name.split("_")[-1]


@register.simple_tag
def check_if_logged_user_can_delete_another_user(logged_user, user_to_delete, server):
    if check_if_logged_user_can_delete_user(logged_user, user_to_delete, server) == True:
        return True
    else:
        return False
    

@register.simple_tag
def check_if_logged_user_have_permission(logged_user, server, permission):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    user_group = [group for group in server_groups if logged_user in group.user_set.all()]
    if permission in user_group[0].permissions.all():
        return True
    else:
        return False



@register.simple_tag
def user_group_all_data(user, server):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    user_group = [group for group in server_groups if user in group.user_set.all()]
    return user_group[0]


@register.simple_tag
def check_if_logged_user_can_change_another_users_group(logged_user, user_to_change, server, destined_group):
    if check_if_logged_user_can_change_users_group(logged_user, user_to_change, server, destined_group) == True:
        return True
    else:
        return False
    

@register.simple_tag
def check_if_logged_user_have_edit_room_permission(logged_user, server):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    user_group = [group for group in server_groups if logged_user in group.user_set.all()]
    permission = Permission.objects.get(codename='edit_rooms_in_server')
    if permission in user_group[0].permissions.all():
        return True
    else:
        return False
    

@register.simple_tag
def check_if_room_invite_exist(receiver, server):
    server_invite = ServerInvite.objects.get(receiver=receiver, server=server)
    if server_invite:
        return True
    else:
        return False
    
