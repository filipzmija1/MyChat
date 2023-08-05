from django import template
from django.contrib.auth.models import Group

from viperchat.utils import check_if_logged_user_can_delete_user, check_if_logged_user_can_change_users_group


register = template.Library()

@register.filter
def split_group_name(name):
    return name.split("_")[-1]


@register.filter
def group_users(group):
    return group.user_set.all()


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
def user_group_all_data(user, server):
    server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
    user_group = [group for group in server_groups if user in group.user_set.all()]
    return user_group[0]


@register.simple_tag
def check_if_logged_user_can_change_another_users_group(logged_user, user_to_change, server):
    if check_if_logged_user_can_change_users_group(logged_user, user_to_change, server) == True:
        return True
    else:
        return False