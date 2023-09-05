from typing import Any, Dict, Optional
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm, model_to_dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.views.generic.base import RedirectView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.utils import timezone

from .models import Room, Notification, FriendRequest, ServerInvite, Message, ServerPermissionSettings, Server, \
                 UserPermissionSettings
from .forms import ResetPasswordForm, SearchForm, SendMessageForm, ServerPermissionsForm, ServerEditForm, \
                UserPermissionForm, SearchUserForm
from .permissions import *
from .context_processor import *
from .utils import check_if_logged_user_can_delete_user, set_masters_permissions, initial_server_permissions, \
            set_moderators_permissions, set_members_permissions, check_if_logged_user_can_change_users_group, set_permission


User = get_user_model()


class HomePage(View):
    """
    Start page view with links
    """
    template_name = 'viperchat/base.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class CreateServer(LoginRequiredMixin, CreateView):
    model = Server
    fields = ['name', 'description', 'is_private']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        permission_settings = ServerPermissionSettings.objects.create()
        form.instance.permission_settings = permission_settings
        server = form.save()
        server.users.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('server_initial', kwargs={'pk': self.object.pk})
    

class GiveInitialPermissions(LoginRequiredMixin, CreateView):
    """
    Creates one room(general), server  groups and gives them default permissions
    """
    model = Room
    fields = []

    def get_object(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        if self.request.user == server.creator:
            return server
        else:
            raise PermissionDenied
    
    def get(self, request, *args, **kwargs):
        server = self.get_object()
        room = Room.objects.create(name='general', server=server)
        # Create server groups
        server_owners, created = Group.objects.get_or_create(name=f'{server.name}_owners')
        server_masters, is_created = Group.objects.get_or_create(name=f'{server.name}_masters')
        server_moderators, status = Group.objects.get_or_create(name=f'{server.name}_moderators')  
        server_members, created = Group.objects.get_or_create(name=f'{server.name}_members')
        
        server_owners.user_set.add(self.request.user)

        # Give initial permissions to server groups - permissions.py file
        initial_server_permissions(server_owners, server_masters, server_moderators, server_members)

        return redirect(reverse('server_detail', kwargs={'pk': server.pk}))
    

class ServerLeaveConfirm(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    If logged in user is one only owner in server he cant leave unless there is no others in server
    """
    model = Server
    template_name = 'viperchat/server_leave_confirm.html'

    def test_func(self):
        if self.request.user in self.get_object().users.all():
            return True
        raise PermissionDenied

    def get_object(self):
        server = Server.objects.get(id=self.kwargs['pk'])
        return server

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        if 'accept' in self.request.POST:
            return redirect(reverse('server_leave', kwargs={'pk': server.id}))
        if 'decline' in self.request.POST:
            return redirect(reverse('server_detail', kwargs={'pk': server.id}))

    def get_context_name(self, **kwargs):
        context = super().get_context_name(**kwargs)
        server = self.get_object()
        context['server'] = server
        context['server_groups'] = Server.objects.filter(name__startswith=f'{server.name}_')
        return context
            

class ServerLeave(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Server
    
    def test_func(self):
        server_owners = Group.objects.get(name=f'{self.get_object().name}_owners')
        if self.request.user in server_owners.user_set.all() and self.get_object().users.all().count() == 1:
            return True
        if self.request.user in server_owners.user_set.all() and server_owners.user_set.all().count() > 1:
            return True
        if self.request.user in server_owners.user_set.all() and \
        server_owners.user_set.all().count() == 1 and \
        self.get_object().users.all().count() > 1:
            return False
        if self.request.user in self.get_object().users.all():
            return True   

    def get_object(self):
        server = Server.objects.get(id=self.kwargs['pk'])
        return server
    
    def get(self, *args, **kwargs):
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        user_group = [group for group in server_groups if self.request.user in group.user_set.all()][0]
        self.get_object().users.remove(self.request.user)
        user_group.user_set.remove(self.request.user)
        return redirect(reverse('home'))

    def get_context_name(self, **kwargs):
        context = super().get_context_name(**kwargs)
        server = self.get_object()
        context['server'] = server
        return context


class ServerDetails(LoginRequiredMixin, DetailView):
    model = Server
    context_object_name = 'server'
    template_name = 'viperchat/server_detail.html'

    def get_object(self):
        return Server.objects.get(id=self.kwargs['pk'])

    def get_queryset(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        if self.request.user in server.users.all():
            return super().get_queryset()
        elif server.is_private == False:
            return super().get_queryset()
        else:
            raise PermissionDenied
        
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        owners_group = Group.objects.get(name=f'{self.get_object().name}_owners')
        context['server_groups'] = server_groups
        context['server'] = self.get_object()
        context['owners_group'] = owners_group
        return context
            

class CreateRoom(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Room
    fields = ['name', 'description', 'is_private']

    def test_func(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        create_permission = Permission.objects.get(codename='create_room_in_server')
        #   Check if user has permission to create room
        for group in server_groups:
            if self.request.user in group.user_set.all() and create_permission in group.permissions.all():
                return True
        raise PermissionDenied

    def get_object(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        return server

    def form_valid(self, form):
        form.instance.server = self.get_object()
        form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('room_detail', kwargs={'pk': self.object.pk, 'server_id': self.get_object().id})
        

class RoomEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Room
    fields = ['name', 'description', 'is_private']
    template_name = 'viperchat/room_edit.html'

    def test_func(self):
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().server.name}_')
        permission = Permission.objects.get(codename='edit_rooms_in_server')
        logged_user_group = [group for group in server_groups if self.request.user in group.user_set.all()]
        #   Check if user has permission to edit room data
        if permission in logged_user_group[0].permissions.all():
            return True
        raise PermissionDenied
    
    def get_object(self):
        room = Room.objects.get(id=self.kwargs['pk'])
        return room
    
    def get_success_url(self):
        return reverse('room_detail', kwargs={'server_id': self.get_object().server.id, 'pk':self.get_object().id} )


class DeleteMessage(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    logged user or room moderator can delete message in room
    """
    model = Message

    def test_func(self):
        logged_user = self.request.user
        if logged_user == self.get_object().author:
            return True
        else:
            server = self.get_object().room.server
            delete_message_permission = Permission.objects.get(codename='delete_message_from_server')
            server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
            for group in server_groups:
                if logged_user in group.user_set.all() and delete_message_permission in group.permissions.all():
                    return True
        raise PermissionDenied

    def get_object(self, *args, **kwargs):
        message_id = self.kwargs['pk']
        message = Message.objects.get(id=message_id)
        return message
        
    def get_success_url(self):
        room = self.get_object().room
        if room:
            return reverse('room_detail', kwargs={'pk': room.pk, 'server_id': room.server.id})
        else:
            return reverse('user_detail', kwargs={'username': self.get_object().message_receiver})
        

class ServerList(ListView):
    """
    Shows every room
    """
    model = Server
    paginate_by = 20


class JoinServer(LoginRequiredMixin, UpdateView):
    """
    Allows user to join to public room
    """
    model = Server

    def get_object(self, *args, **kwargs):
        server_id = self.kwargs['pk']
        server = Server.objects.get(pk=server_id)
        return server
    
    def get(self, request, *args, **kwargs):
        server = self.get_object()
        member_group = Group.objects.get(name=f'{server.name}_members')
        if server.is_private == False:
            server.users.add(self.request.user)
            member_group.user_set.add(self.request.user)
            server.save()
            return redirect(reverse('server_detail', kwargs={'pk': server.pk}))
        else:
            raise PermissionDenied


class ServerInviteSend(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create invitation to public server
    """
    model = ServerInvite

    def test_func(self):
        invite_to_server_permission = Permission.objects.get(codename='send_invitation')
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        invite_receiver = User.objects.get(username=self.kwargs['username'])
        user_group = [group for group in server_groups if self.request.user in group.user_set.all()][0]
        invite = ServerInvite.objects.filter(server=self.get_object(), receiver=invite_receiver)
        #   Check if server invite already exists
        if invite:
            raise PermissionDenied
        if invite_to_server_permission in user_group.permissions.all():
            return True
        if invite_receiver in self.object().users.all():
            raise PermissionDenied
        raise PermissionDenied

    def get_object(self):
        server = Server.objects.get(id=self.kwargs['pk'])
        return server

    def get(self, *args, **kwargs):
        invite_receiver = User.objects.get(username=self.kwargs['username'])
        ServerInvite.objects.create(server=self.get_object(), invitation_sender=self.request.user, receiver=invite_receiver)
        return redirect(reverse('server_invite', kwargs={'pk': self.get_object().id}))


class ServerInviteDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Only invitation sender is able to delete server invitations
    """
    model = ServerInvite

    def test_func(self):
        invite = ServerInvite.objects.get(id=self.kwargs['invite_id'])
        if invite.invitation_sender == self.request.user:
            return True
        raise PermissionDenied
    
    def get(self, *args, **kwargs):
        invite = ServerInvite.objects.get(id=self.kwargs['invite_id'])
        invite.delete()
        return redirect(reverse('server_invite', kwargs={'pk': self.kwargs['pk']}))


class SearchUserToInvite(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    This view is destined to search users for invite them
    """
    template_name = 'viperchat/server_invite.html'
    form_class = SearchUserForm
    
    def test_func(self):
        invite_to_server_permission = Permission.objects.get(codename='send_invitation')
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        user_group = [group for group in server_groups if self.request.user in group.user_set.all()][0]
        if invite_to_server_permission in user_group.permissions.all():
            return True
        raise PermissionDenied

    def get_object(self):
        server = Server.objects.get(id=self.kwargs['pk'])
        return server

    def form_valid(self, form):
        search_value = form.cleaned_data['search']
        search_result = None
        if search_value:
            search_result = User.objects.filter(username__startswith=search_value)
        return render(self.request, 'viperchat/server_invite.html', self.get_context_data(form=form, result=search_result))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['server_invites'] = ServerInvite.objects.filter(server=self.get_object())
        context['server'] = self.get_object()
        context['server_groups'] = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        return context


class RoomDetail(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
    """
    Shows room details and gives posibility to write message in chatroom
    """
    model = Room
    context_object_name = 'room'
    form_class = SendMessageForm
    template_name = 'viperchat/room_detail.html'

    def test_func(self):
        server_id = self.kwargs['server_id']
        server = Server.objects.get(id=server_id)
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        room = self.get_object()
        show_private_room_permission = Permission.objects.get(codename='display_private_room_data')
        send_message_permission = Permission.objects.get(codename='send_messages_in_server')
        logged_user_group = [group for group in server_groups if self.request.user in group.user_set.all()]
        if not send_message_permission in logged_user_group[0].permissions.all():
            raise PermissionDenied
        if room.is_private == True and show_private_room_permission in logged_user_group[0].permissions.all():
            return True
        elif room.is_private == False and self.request.user in server.users.all():
            return True
        else:
            raise PermissionDenied

    def get_object(self, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        return room
        
    def get_context_data(self,  *args, **kwargs):
        context = super().get_context_data(**kwargs)
        logged_user = self.request.user
        server_id = self.kwargs['server_id']
        server = Server.objects.get(id=server_id)
        delete_message_permission = Permission.objects.get(codename='delete_message_from_server')
        send_message_permission = Permission.objects.get(codename='send_messages_in_server')
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')    # Get all server groups
        context['all_messages'] = Message.objects.filter(room=self.get_object())
        context['form'] = SendMessageForm()
        context['server'] = self.get_object().server
        context['server_groups'] = server_groups
        context['send_message_permission'] = send_message_permission
        context['room_id'] = self.get_object().id
        context['server_id'] = self.get_object().server.id
        for group in server_groups:
            if logged_user in group.user_set.all() and delete_message_permission in group.permissions.all():
                context["deleters"] = group.user_set.all()
        return context
    

class RoomMessagesManage(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    User can manage others messages
    """
    model = Message
    template_name = 'viperchat/room_messages_manage.html'
    context_object_name = 'room_messages'

    def test_func(self):
        delete_message_permission = Permission.objects.get(codename='delete_message_from_server')
        server = Server.objects.get(id=self.kwargs['server_id'])
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        user_group = [group for group in server_groups if self.request.user in group.user_set.all()]
        if delete_message_permission in user_group[0].permissions.all():
            return True
        return False
    
    def get_queryset(self):
        room = Room.objects.get(id=self.kwargs['pk'])
        messages = Message.objects.filter(room=room).order_by('-date_created')
        return messages

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['server'] = Server.objects.get(id=self.kwargs['server_id'])
        return context


class RoomUserOwnMessages(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Delete and editing own messages
    """
    model = Message
    template_name = 'viperchat/room_user_own_messages.html'
    context_object_name = 'user_messages'

    def test_func(self):
        room = Room.objects.get(id=self.kwargs['pk'])
        if self.request.user in room.server.users.all():
            return True
        return False

    def get_queryset(self):
        room = Room.objects.get(id=self.kwargs['pk'])
        user_messages_in_room = Message.objects.filter(room=room, author=self.request.user)
        return user_messages_in_room
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['server'] = Server.objects.get(id=self.kwargs['server_id'])
        return context


class ServerEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Server
    form_class = ServerEditForm
    template_name = 'viperchat/server_edit.html'

    def test_func(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        owners_group = Group.objects.get(name=f'{server.name}_owners')
        if self.request.user in owners_group.user_set.all():
            return True
        else: 
            raise PermissionDenied
        
    def get_success_url(self):
        return reverse('server_detail', kwargs={'pk': self.object.pk})


class ServerGroupsManagement(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Display groups permissions settings
    """
    model = ServerPermissionSettings
    template_name = 'viperchat/server_groups_management.html'
    form_class = ServerPermissionsForm

    def test_func(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        owners_group = Group.objects.get(name=f'{server.name}_owners')
        if self.request.user in owners_group.user_set.all():
            return True
        else:
            raise PermissionDenied
    
    def get_object(self):
        server = Server.objects.get(id=self.kwargs['pk'])
        permission_settings = server.permission_settings
        return permission_settings
    
    def get_success_url(self):
        #   Redirects to URL which change permissions
        return reverse('permissions_change', kwargs={'pk': self.kwargs['pk']})


class ServerPermissionChange(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Saves groups permissions changes
    """
    model = Group
    fields = []

    def test_func(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        owners_group = Group.objects.get(name=f'{server.name}_owners')
        if self.request.user in owners_group.user_set.all():
            return True
        else:
            raise PermissionDenied
    
    def get_object(self):
        server = Server.objects.get(id=self.kwargs['pk'])
        return server
    
    def get(self, *args, **kwargs):
        #   Set groups permissions functions are in utils.py file
        set_masters_permissions(self.get_object())
        set_moderators_permissions(self.get_object())
        set_members_permissions(self.get_object())
        return redirect(reverse('server_detail', kwargs={'pk': self.get_object().id}))
        

class ServerUsersManage(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Display server's users and give possibility to delete them from server or change their groups
    """
    model = User
    context_object_name = 'users'
    template_name = 'viperchat/server_users_list.html'
    
    def test_func(self):
        delete_users_permission = Permission.objects.get(codename='delete_user_from_server')
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        for group in server_groups:
            if self.request.user in group.user_set.all() and delete_users_permission in group.permissions.all():
                return True
        raise PermissionDenied

    def get_object(self, *args, **kwargs):
        return Server.objects.get(id=self.kwargs['server_id'])
    
    def get_queryset(self):
        logged_user = self.request.user
        if logged_user in self.get_object().users.all():
            return self.get_object().users.all()
        else:
            raise PermissionDenied
        
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        context['server_groups'] = server_groups
        context['server'] = self.get_object()
        return context


class UserGroupEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit user groups to change his permissions
    """
    model = User
    fields = []

    def test_func(self):
        server = Server.objects.get(id=self.kwargs['server_id'])
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        edit_group_permission = Permission.objects.get(codename='change_user_group')
        for group in server_groups:
            if self.request.user in group.user_set.all() and edit_group_permission in group.permissions.all():
                return True
        raise PermissionDenied
    
    def get_object(self):
        user_username = self.kwargs['username']
        user_to_change = User.objects.get(username=user_username)
        return user_to_change

    def get(self, *args, **kwargs):
        group = Group.objects.get(name=self.kwargs['name'])
        user_to_change = self.get_object()
        server = Server.objects.get(id=self.kwargs['server_id'])
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        #   Get changing user group
        user_to_change_group = [group for group in server_groups if user_to_change in group.user_set.all()]
        #   function details in utils.py file
        if check_if_logged_user_can_change_users_group(self.request.user, user_to_change, server, group) == True:
            user_to_change_group[0].user_set.remove(user_to_change)
            group.user_set.add(user_to_change)
            return redirect(reverse('server_users_list', kwargs={'server_id': server.id}))
        else:
            raise PermissionDenied


class UserServerList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Display servers which user belongs to
    """
    model = Server
    context_object_name = 'servers'
    template_name = 'viperchat/user_server_list.html'

    def test_func(self):
        user_username = self.kwargs['username']
        if self.request.user.username == user_username:
            return True
        else:
            return False
    
    def get_queryset(self):
        return Server.objects.filter(users=self.request.user)


class DeleteUserFromServer(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Deletes user from server and server's groups
    """
    model = Server
    fields = []

    def test_func(self):
        server_id = self.kwargs['server_id']
        server = Server.objects.get(id=server_id)
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        delete_permission = Permission.objects.get(codename='delete_user_from_server')
        for group in server_groups:
            if self.request.user in group.user_set.all() and delete_permission in group.permissions.all():
                return True
        raise PermissionDenied

    def get_object(self):
        user_username = self.kwargs['username']
        user_to_delete = User.objects.get(username=user_username)
        return user_to_delete

    def get(self, request, *args, **kwargs):
        server_id = self.kwargs['server_id']
        server = Server.objects.get(id=server_id)
        logged_user = self.request.user
        user_to_delete = self.get_object()
        owners_group = Group.objects.get(name=f'{server.name}_owners')
        masters_group = Group.objects.get(name=f'{server.name}_masters')
        members_group = Group.objects.get(name=f'{server.name}_members')
        moderators_group = Group.objects.get(name=f'{server.name}_moderators')
        #   check_if_logged_user_can_delete_user is in utils.py file
        if check_if_logged_user_can_delete_user(logged_user, user_to_delete, server) == True:
            owners_group.user_set.remove(user_to_delete)
            masters_group.user_set.remove(user_to_delete)
            members_group.user_set.remove(user_to_delete)
            moderators_group.user_set.remove(user_to_delete)
            server.users.remove(user_to_delete)
            return redirect(reverse('server_users_list', kwargs={'server_id': server_id}))
        else:
            raise PermissionDenied


class UserProfile(LoginRequiredMixin, FormMixin, DetailView):
    """
    Shows user profile
    """
    model = User
    template_name = 'viperchat/user_profile.html'
    context_object_name = 'user'
    form_class = SendMessageForm

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user
    
    def get_context_data(self, **kwargs):
        """
        friend request display add friend or cancel friend request
        """
        context = super().get_context_data(**kwargs)
        friend_request = FriendRequest.objects.filter(sender=self.request.user, receiver=self.get_object())
        friend_request_mirror = FriendRequest.objects.filter(sender=self.get_object(), receiver=self.request.user)
        user_profile_settings = UserPermissionSettings.objects.get(user=self.get_object())
        context['user_settings'] = user_profile_settings
        context['friend_request'] = friend_request
        context['friend_request_mirror'] = friend_request_mirror
        context['username'] = self.get_object().username
        if self.request.user in self.get_object().friends.all():    # Display chat
            friend_messages = Message.objects.filter(author=self.get_object(), message_receiver=self.request.user)
            logged_user_messages = Message.objects.filter(author=self.request.user, message_receiver=self.get_object())
            context['chat'] = (friend_messages | logged_user_messages).order_by('date_created')
            return context
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            message = form.cleaned_data['message']
            author = self.request.user
            Message.objects.create(author=author, content=message, message_receiver=self.get_object())
            return redirect(reverse('user_detail', kwargs={'username': self.get_object().username}))
        else:
            return redirect(reverse('user_detail', kwargs={'username': self.get_object().username}))
        

class UserServerInvitesList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """"
    Display user's server join requests
    """
    model = ServerInvite
    template_name = 'viperchat/server_invites_list.html'
    context_object_name = 'invites'

    def test_func(self):
        if self.get_object() == self.request.user:
            return True
        raise PermissionDenied
    
    def get_object(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user
    
    def get_queryset(self):
        invites = ServerInvite.objects.filter(receiver=self.get_object())
        return invites
    

class ServerInviteDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ServerInvite
    template_name = 'viperchat/server_invite_detail.html'
    context_object_name = 'invite'

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if self.request.user == user:
            return True
        raise PermissionDenied
    
    def get_object(self):
        invite = ServerInvite.objects.get(id=self.kwargs['pk'])
        return invite
    
    def post(self, request,*args, **kwargs):
        invite = self.get_object()
        members_group = Group.objects.get(name=f'{invite.server.name}_members')
        if 'accept_button' in self.request.POST:
            invite.server.users.add(self.request.user)
            members_group.user_set.add(self.request.user)
            invite.status = 'accepted'
        if 'decline_button' in self.request.POST:
            invite.status = 'declined'
        invite.save()
        #   Refresh for signals work
        invite.refresh_from_db() 
        invite.delete()
        return redirect('user_server_invites', username=self.request.user.username)


class MessageEdit(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'viperchat/message_edit.html'
    fields = ['content']

    def get_queryset(self):
        message_id = self.kwargs['pk']
        message = Message.objects.get(id=message_id)
        if message.author != self.request.user:
            raise PermissionDenied
        else:
            return super().get_queryset()

    def form_valid(self, form):
        form.instance.date_edited = timezone.now()
        form.save()
        return redirect(self.get_success_url())
        
    def get_success_url(self):
        """
        Success url depends on if chat is in room or between two users
        """
        message_id = self.kwargs['pk']
        message = Message.objects.get(id=message_id)
        if message.room:
            return reverse('room_detail', kwargs={'pk': message.room.id, 'server_id': message.room.server.id})
        else:
            return reverse('user_detail', kwargs={'username': message.message_receiver.username})


class UserProfileEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    This view is destined to change user data
    """
    model = User
    template_name = 'viperchat/user_edit.html'
    context_object_name = 'user'
    fields = ['first_name', 'last_name']

    def test_func(self):
        username = self.kwargs['username']
        logged_user = self.request.user
        if username != logged_user.username:
            raise PermissionDenied
        else:
            return True

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user
    
    def get_success_url(self):
        return reverse('user_detail', kwargs={'username': self.request.user.username})


class UserProfilePermissions(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserPermissionSettings
    template_name = 'viperchat/user_permissions.html'
    form_class = UserPermissionForm

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if user == self.request.user:
            return True
        raise PermissionDenied
    
    def get_object(self):
        user_permission_settings = UserPermissionSettings.objects.get(user=self.request.user)
        return user_permission_settings

    def form_valid(self, form):
        user_profile_display_permission_setting = form.cleaned_data['everyone_see_your_profile']
        only_friend_see_profile_permission = Permission.objects.get(codename='friends_see_profile')
        if user_profile_display_permission_setting == 'Allowed':
            self.request.user.user_permissions.remove(only_friend_see_profile_permission)
        if user_profile_display_permission_setting == 'Forbidden':
            self.request.user.user_permissions.add(only_friend_see_profile_permission)
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('edit_profile', kwargs={'username': self.get_object().user.username})


class ChangePassword(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """
    This view is destined to change user password (you can do this by enter your old password)
    """
    model = User
    template_name = 'viperchat/edit_password.html'
    context_object_name = 'user'
    form_class = ResetPasswordForm
    success_message = 'Password changed successfully'

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        logged_user = self.request.user
        if username != logged_user.username:
            raise PermissionDenied
        return user

    def form_valid(self, form):
        old_password = form.cleaned_data['old_password']
        new_password = form.cleaned_data['new_password']
        confirm_password = form.cleaned_data['confirm_password']
        user = self.request.user
        if check_password(old_password, user.password):
            if new_password == confirm_password:
                try:
                    validate_password(new_password, user=user)
                except Exception as e:
                    form.add_error('new_password', str(e))
                    return self.form_invalid(form)
                user.set_password(new_password)
                user.save()
                return redirect(reverse('account_logout'))
            else:
                form.add_error('confirm_password', 'New password and confirm password do not match')
                return self.form_invalid(form)
        else:
            form.add_error('old_password', 'Old password does not match')
            return self.form_invalid(form)


class SearchUserOrRoom(FormView):
    """
    This view is destined to search users and/or rooms
    """
    form_class = SearchForm
    template_name = 'viperchat/search_form.html'

    def form_valid(self, form):
        search_by = form.cleaned_data['search_by']
        search_value = form.cleaned_data['search']
        search_result = None
        if search_value:
            if search_by == 'room':
                search_result = Room.objects.filter(
                    Q(name__icontains=search_value) | 
                    Q(name__startswith=search_value),
                    is_private=False)
            if search_by == 'user':
                search_result = User.objects.filter(
                    Q(username__icontains=search_value) | 
                    Q(username__startswith=search_value))
        return render(self.request, 'viperchat/search_form.html', self.get_context_data(form=form, search_result=search_result))
    

class DeleteFriend(LoginRequiredMixin, View):
    """
    View destined to delete friend from friendlist and from friends groups
    """
    def get(self, request, *args, **kwargs):
        user_username = self.kwargs['username']
        user_to_remove = User.objects.get(username=user_username)
        logged_user = self.request.user
        logged_user_friends_group, created = Group.objects.get_or_create(name=f'{logged_user}_friends')
        removing_user_friends_group, created = Group.objects.get_or_create(name=f'{user_to_remove}_friends')
        if not logged_user.friends.filter(username=user_to_remove.username).exists():
            raise PermissionDenied
        else:
            logged_user.friends.remove(user_to_remove)
            logged_user_friends_group.user_set.remove(user_to_remove)
            removing_user_friends_group.user_set.remove(logged_user)
            return redirect(reverse('user_detail', kwargs={'username': logged_user.username}))
        
        
class FriendNotifiaction(LoginRequiredMixin, CreateView):
    """
    Concerns only friend request notifcations
    """
    model = FriendRequest
    fields = []

    def get_object(self):
        user_username = self.kwargs['username']
        user = User.objects.get(username=user_username)
        logged_user = self.request.user
        if user == logged_user:
            raise PermissionDenied
        else:
            return user
        
    def get(self, request, *args, **kwargs):
        sender = self.request.user
        receiver = self.get_object()
        description = f"{self.request.user.username} wants to join your friendlist"

        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists() \
        or FriendRequest.objects.filter(sender=receiver, receiver=sender).exists() \
        or receiver in sender.friends.all():
            raise PermissionDenied
        else:
            FriendRequest.objects.create(sender=sender, receiver=receiver, description=description)
            return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('user_detail', kwargs={'username': self.get_object().username})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context


class NotificationList(LoginRequiredMixin, ListView):
    """
    Show user's notifications
    """
    model = Notification

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user_username = self.kwargs['username']      # Get user's username from the URL
        user = User.objects.get(username=user_username)
        logged_user = self.request.user
        notifications = Notification.objects.filter(receiver=user).order_by('-date_created')
        if user != logged_user:
            raise PermissionDenied
        else:
            context['notifications'] = notifications
            return context
        

class NotificationUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Changes notification is_read status
    """
    model = Notification

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if user == self.request.user:
            return True
        raise PermissionDenied
    
    def get_object(self):
        notification = Notification.objects.get(id=self.kwargs['pk'])
        return notification

    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.is_read == False:
            notification.is_read = True
        notification.save()
        return redirect(reverse('notification_detail', kwargs={'username': self.request.user.username,
                                                             'pk': notification.id}))


class NotificationSetUnread(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Set notification to unread
    """
    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if user == self.request.user:
            return True
        raise PermissionDenied
    
    def get_object(self):
        notification = Notification.objects.get(id=self.kwargs['pk'])
        return notification

    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.is_read == True:
            notification.is_read = False
        notification.save()
        return redirect(reverse('notification_list', kwargs={'username': self.request.user.username}))


class NotificationsReadList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Display notifications already read
    """
    model = Notification
    template_name = 'viperchat/notification_read_list.html'

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if user == self.request.user:
            return True
        raise PermissionDenied
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = Notification.objects.filter(receiver=self.request.user)
        context['notifications'] = notifications
        return context
    

class Notifications(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Navigate through Notifications
    """
    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if user == self.request.user:
            return True
        raise PermissionDenied
    
    def get(self, request,  *args, **kwargs):
        notifications = Notification.objects.filter(receiver=self.request.user)
        return render(request, 'viperchat/notifications.html', {'notifications': notifications})


class NotificationUnreadList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Display unread notifications
    """
    model = Notification
    template_name = 'viperchat/notification_unread_list.html'

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        if user == self.request.user:
            return True
        raise PermissionDenied
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = Notification.objects.filter(receiver=self.request.user)
        context['notifications'] = notifications
        return context
    

class NotificationDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Notification
    context_object_name = 'notification'

    def test_func(self):
        if self.request.user == self.get_object().receiver:
            return True
        raise PermissionDenied

    def get_object(self):
        notification = Notification.objects.get(id=self.kwargs['pk'])
        return notification
    

class NotificationDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Notification

    def test_func(self):
        if self.request.user == self.get_object().receiver:
            return True
        raise PermissionDenied
    
    def get_object(self):
        notification = Notification.objects.get(id=self.kwargs['pk'])
        return notification
    
    def get(self, *args, **kwargs):
        #   Dont need to confirm delete
        return self.post(*args, **kwargs)
    
    def get_success_url(self):
        return reverse('notification_list', kwargs={'username': self.request.user})


class AllNotificationsDelete(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Delete user's all notifications
    """
    model = Notification

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        notifications = Notification.objects.filter(receiver=self.request.user)
        if notifications.count() == 0:
            return False
        if self.request.user == user:
            return True
        raise PermissionDenied
    
    def get(self, *args, **kwargs):
        notifications =Notification.objects.filter(receiver=self.request.user)
        notifications.delete()
        return redirect(self.get_success_url())    
    
    def get_success_url(self):
        return reverse('notification_list', kwargs={'username': self.request.user})
    

class NotifiacationsDeleteConfirm(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Delete all notifications must be confirm
    """
    model = Notification
    template_name = 'viperchat/notification_delete_confirm.html'

    def test_func(self):
        user = User.objects.get(username=self.kwargs['username'])
        user = User.objects.get(username=self.kwargs['username'])
        notifications = Notification.objects.filter(receiver=self.request.user)
        if notifications.count() == 0:
            return False
        if self.request.user == user:
            return True
        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if 'accept' in self.request.POST:
            return redirect(reverse('all_notifications_delete', kwargs={'username': self.request.user}))
        else:
            return redirect(reverse('notification_list', kwargs={'username': self.request.user}))
    

class FriendRequestList(LoginRequiredMixin, ListView):
    """
    Show user's friend requests
    """
    model = FriendRequest

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user_username = self.kwargs['username']      # Get user's username from the URL
        user = User.objects.get(username=user_username)
        logged_user = self.request.user
        friend_requests = FriendRequest.objects.filter(receiver=user).order_by('-date_created')
        if user != logged_user:
            raise PermissionDenied
        else:
            context['friend_requests'] = friend_requests
            return context
        

class FriendRequestAnswer(LoginRequiredMixin, UpdateView):
    """
    See friend request details and changes request status plus adding to friends or decline.
    """
    model = FriendRequest
    context_object_name = 'friend_request'
    fields = []
    template_name = 'viperchat/friendrequest_detail.html'

    def get_object(self, queryset=None):
        request_id = self.kwargs['pk']
        friend_request = FriendRequest.objects.get(pk=request_id)
        if self.request.user != friend_request.receiver:
            raise PermissionDenied
        else:
            return friend_request
        
    def form_valid(self, form):
        """
        If user accepts
          """
        friend_request = form.instance
        if 'accept_button' in self.request.POST:
            friend_request.status = 'accepted'
            friends_group, created = Group.objects.get_or_create(name=f'{self.request.user}_friends')
            sender_friends_group, created = Group.objects.get_or_create(name=f'{friend_request.sender}_friends')
            sender_friends_group.user_set.add(self.request.user)
            friends_group.user_set.add(friend_request.sender)
            self.request.user.friends.add(friend_request.sender)
            #   Create accepted request notification
            Notification.objects.create(
                description=f'{self.request.user} has accepted your friend invite.', 
                receiver=friend_request.sender)
        elif 'decline_button' in self.request.POST:
            friend_request.status = 'canceled'
            Notification.objects.create(
                description=f'{self.request.user} has declined your friend invite.',
                receiver=friend_request.sender)
        form.save()
        friend_request.delete()
        return redirect('user_detail', username=self.request.user.username)
    

class FriendRequestDelete(LoginRequiredMixin, DeleteView):
    """
    Delete friend invitation
    """
    model = FriendRequest

    def get_object(self):
        logged_user = self.request.user
        friend_request_id = self.kwargs['pk']
        friend_request = FriendRequest.objects.get(pk=friend_request_id)
        if logged_user != friend_request.sender:
            raise PermissionDenied
        else:
            return friend_request
        
    def get(self, request, *args, **kwargs):
        receiver = self.get_object().receiver
        self.get_object().delete()
        return redirect('user_detail', username=receiver.username)
    