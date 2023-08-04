from typing import Any, Dict
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView

from .models import Server


def get_create_room_permission(request):
    content_type = ContentType.objects.get_for_model(Server)
    permission = Permission.objects.get(codename='create_room_in_server', content_type=content_type)
    return {'create_permission': permission}


def get_homepage(request):
    return {'welcome': 'Welcome to great chat'}


def get_server_list(request):
    public_servers = Server.objects.filter(is_private=False)
    return {'server_list': public_servers}


def get_edit_permissions(request):
    permission = Permission.objects.get(codename='edit_permissions_in_server')
    return {'edit_permissions': permission}


def get_delete_user(request):
    permission = Permission.objects.get(codename='delete_user_from_server')
    return {'delete_users_permission': permission}