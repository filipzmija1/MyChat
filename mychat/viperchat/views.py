from typing import Any, Dict, Optional
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.utils import timezone

from .models import Room, Notification, FriendRequest, RoomInvite, Message, ServerPermissionSettings, Server
from .forms import ResetPasswordForm, SearchForm, RoomManagementForm, SendMessageForm, ServerPermissionsForm, ServerEditForm
from .permissions import *
from .utils import check_if_logged_user_can_delete_user


User = get_user_model()


class HomePage(View):
    """Start page view with links"""
    template_name = 'viperchat/base.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'welcome': 'Welcome to great chat',
        }
        return render(request, self.template_name, context)
    

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
    """Creates one room(general), server groups and gives them default permissions"""
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
        permission = Permission.objects.get(codename='create_room_in_server')
        server_groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        context['create_permission'] = permission
        context['server_groups'] = server_groups
        context['server'] = self.get_object()
        return context
            

class CreateRoom(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Room
    fields = ['name', 'description', 'is_private']

    def test_func(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')
        create_permission = Permission.objects.get(codename='create_room_in_server')
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
        return reverse('server_detail', kwargs={'pk': self.get_object().pk, 'server_id': self.object.pk})
        

class DeleteMessage(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """logged user or room moderator can delete message in room"""
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
    """Shows every room"""
    model = Server
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        public_servers = Server.objects.filter(is_private=False)
        context['server_list'] = public_servers
        return context


class JoinServer(LoginRequiredMixin, UpdateView):
    """Allows user to join to public room"""
    model = Room

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
    

class RoomDetail(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
    """Shows room details and gives posibility to write message in chatroom"""
    model = Room
    context_object_name = 'room'
    form_class = SendMessageForm

    def test_func(self):
        server_id = self.kwargs['server_id']
        server = Server.objects.get(id=server_id)
        if self.request.user in server.users.all():
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
        server_groups = Group.objects.filter(name__startswith=f'{server.name}_')    # Get all server groups
        context['messages'] = Message.objects.filter(room=self.get_object())
        context['form'] = SendMessageForm()
        context['server'] = self.get_object().server
        for group in server_groups:
            if logged_user in group.user_set.all() and delete_message_permission in group.permissions.all():
                context["deleters"] = group.user_set.all()
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            room = self.get_object()
            author = self.request.user
            message = form.cleaned_data['message']
            Message.objects.create(room=room, author=author, content=message)
            return redirect(reverse('room_detail', kwargs={'pk': self.get_object().pk, 'server_id': self.get_object().server.id}))
        else:
            return redirect(reverse('room_detail', kwargs={'pk': self.get_object().pk, 'server_id': self.get_object().server.id}))


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
    model = Server
    template_name = 'viperchat/server_groups_management'

    def test_func(self):
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=server_id)
        owners_group = Group.objects.get(name=f'{server.name}_owners')
        if self.request.user in owners_group.user_set.all():
            return True
        else:
            raise PermissionDenied
        
    


# class RoomManagement(LoginRequiredMixin, UpdateView):
#     """Here you can set permissions for each group"""
#     model = Room
#     form_class = RoomManagementForm
#     second_form_class = ServerPermissionsForm
#     template_name = 'viperchat/room_management.html'

#     def get_object(self, *args, **kwargs):
#         room_id = self.kwargs['pk']
#         room = Room.objects.get(id=room_id)
#         room_masters = Group.objects.get(name=f'{room.name}_masters')
#         if self.request.user in room_masters.user_set.all():
#             return room
#         else:
#             raise PermissionDenied
        
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['room'] = self.get_object()
#         if 'form' not in context:
#             context['form'] = self.form_class(instance=self.get_object())
#         if 'second_form' not in context:
#             context['second_form'] = self.second_form_class(instance=self.get_object().permission_settings)
#         return context
        
#     def form_valid(self, form):
#         permission_settings_form = ServerPermissionsForm(self.request.POST)
#         permission_settings = self.get_object().permission_settings
#         if form.is_valid() and permission_settings_form.is_valid():
#             moderator_delete_messages_permission = permission_settings_form.cleaned_data['moderators_delete_messages']
#             moderator_delete_user_permission = permission_settings_form.cleaned_data['moderators_delete_user']
#             moderators_send_invite_permission = permission_settings_form.cleaned_data['moderators_send_invitation']
#             members_send_invite_permission = permission_settings_form.cleaned_data['members_send_invitation']
#             #   Get groups
#             moderator_group = Group.objects.get(name=f'{self.get_object().name}_mods')
#             member_group = Group.objects.get(name=f'{self.get_object().name}_members')
#         #   set moderator permissions
#         set_permission(moderator_delete_messages_permission, moderator_group, add_delete_message_permission, remove_delete_message_permission)
#         set_permission(moderators_send_invite_permission, moderator_group, add_send_invitation_permission, remove_send_invitation_permission)
#         #   set member permissions
#         set_permission(members_send_invite_permission, member_group, add_send_invitation_permission, remove_send_invitation_permission)
#         #   Save permissions settings to database
#         permission_settings.moderators_delete_messages = moderator_delete_messages_permission
#         permission_settings.moderators_delete_user = moderator_delete_user_permission
#         permission_settings.moderators_send_invitation = moderators_send_invite_permission
#         permission_settings.members_send_invitation = members_send_invite_permission

#         permission_settings.save()
#         form.save()
#         return redirect(reverse('room_detail', kwargs={'pk': self.get_object().pk}))
    

class RoomRanksDisplay(LoginRequiredMixin, ListView):
    """Show room groups and users belongs to eachone"""
    model = Group
    context_object_name = 'groups'
    template_name = 'viperchat/room_groups_management.html'

    def get_object(self, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        return room

    def get_queryset(self):
        logged_user = self.request.user
        room_owners_group = Group.objects.get(name=f'{self.get_object().name}_masters')
        if logged_user in room_owners_group.user_set.all():
            return Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = self.get_object()
        return context
        

class ServerUsersList(LoginRequiredMixin, ListView):
    """Display room's users and give possibility to delete them from room"""
    model = User
    context_object_name = 'users'
    template_name = 'viperchat/server_users_list.html'

    def get_object(self, *args, **kwargs):
        return Server.objects.get(id=self.kwargs['pk'])
    
    def get_queryset(self):
        logged_user = self.request.user
        if logged_user in self.get_object().users.all():
            return self.get_object().users.all()
        else:
            raise PermissionDenied
        
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        permission = Permission.objects.get(codename='delete_user_from_server')
        for group in groups:
            if self.request.user in group.user_set.all() and permission in group.permissions.all():
                context['remover'] = group.user_set.all()
        context['server'] = self.get_object()
        return context
        

class UserRankDetail(LoginRequiredMixin, DetailView):
    """Show which users belongs to which group"""
    model = Room
    template_name = 'viperchat/rank_management.html'
    fields = []

    def get_object(self, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        logged_user = self.request.user
        room_owners_group = Group.objects.get(name=f'{room.name}_masters')
        if logged_user in room_owners_group.user_set.all():
            return room
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_name = self.kwargs['name']
        context['group'] = Group.objects.get(name=group_name)
        context['room'] = self.get_object()
        context['groups'] = Group.objects.filter(name__startswith=f'{self.get_object().name}_')
        return context
    

class DeleteUserFromServer(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Deletes user from room and takes permissions"""
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
        if check_if_logged_user_can_delete_user(logged_user, user_to_delete, server) == True:
            owners_group.user_set.remove(user_to_delete)
            masters_group.user_set.remove(user_to_delete)
            members_group.user_set.remove(user_to_delete)
            moderators_group.user_set.remove(user_to_delete)
            server.users.remove(user_to_delete)
            return redirect(reverse('server_users_list', kwargs={'pk': server_id}))
        else:
            raise PermissionDenied
        

class UserRankEdit(LoginRequiredMixin, UpdateView):
    """Here you can edit user's groups"""
    model = Room
    fields = []

    def get_object(self):
        edited_user = User.objects.get(username=self.kwargs['username'])
        room = Room.objects.get(id=self.kwargs['pk'])
        masters_group = Group.objects.get(name=f'{room.name}_masters')
        logged_user = self.request.user
        if edited_user in masters_group.user_set.all():
            raise PermissionDenied
        elif logged_user in masters_group.user_set.all():
            return edited_user
        else:
            raise PermissionDenied
    
    def get(self, request, *args, **kwargs):
        edited_user = self.get_object()
        room = Room.objects.get(id=self.kwargs['pk'])
        group_to_promote = Group.objects.get(name=self.kwargs['name'])
        moderators_group = Group.objects.get(name=f'{room.name}_mods')
        members_group = Group.objects.get(name=f'{room.name}_members')
        masters_group = Group.objects.get(name=f'{room.name}_masters')
        if edited_user in group_to_promote.user_set.all() or edited_user in masters_group.user_set.all():
            raise PermissionDenied
        else:
            #   Delete from user group and then add to another
            moderators_group.user_set.remove(edited_user)
            members_group.user_set.remove(edited_user)
            masters_group.user_set.remove(edited_user)
            #   Add to destined group
            group_to_promote.user_set.add(edited_user)
            return redirect(reverse('room_groups_management', kwargs={'pk': room.id}))
        

class UserOwnRooms(LoginRequiredMixin, ListView):
    """Display user own rooms"""
    model = Room
    context_object_name = "user_rooms"
    template_name = 'viperchat/user_own_rooms.html'

    def get_queryset(self):
        logged_user = self.request.user
        rooms = Room.objects.filter(users=logged_user)
        return rooms


class UserProfile(LoginRequiredMixin, FormMixin, DetailView):
    """Shows user profile"""
    model = User
    template_name = 'viperchat/user_profile.html'
    context_object_name = 'user'
    form_class = SendMessageForm

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user
    
    def get_context_data(self, **kwargs):
        """friend request display add friend or cancel friend request"""
        context = super().get_context_data(**kwargs)
        friend_request = FriendRequest.objects.filter(sender=self.request.user, receiver=self.get_object())
        friend_request_mirror = FriendRequest.objects.filter(sender=self.get_object(), receiver=self.request.user)
        context['friend_request'] = friend_request
        context['friend_request_mirror'] = friend_request_mirror
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
        """Success url depends on if chat is in room or between two users"""
        message_id = self.kwargs['pk']
        message = Message.objects.get(id=message_id)
        if message.room:
            return reverse('room_detail', kwargs={'pk': message.room.id, 'server_id': message.room.server.id})
        else:
            return reverse('user_detail', kwargs={'username': message.message_receiver.username})


class UserProfileEdit(LoginRequiredMixin, UpdateView):
    """This view is destined to change user data"""
    model = User
    template_name = 'viperchat/user_edit.html'
    context_object_name = 'user'
    fields = ['first_name', 'last_name']

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        logged_user = self.request.user
        if username != logged_user.username:
            raise PermissionDenied
        return user
    
    def get_success_url(self):
        return reverse('user_detail', kwargs={'username': self.request.user.username})
    

class ChangePassword(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """This view is destined to change user password (you can do this by enter your old password)"""
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
    """This view is destined to search users and/or rooms"""
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
    """View destined to delete friend from friendlist and from friends groups"""
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
    """Concerns only friend request notifcations"""
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
    """Show user's notifications"""
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
        

class FriendRequestList(LoginRequiredMixin, ListView):
    """Show user's friend requests"""
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
    """See friend request details and changes request status plus adding to friends or decline."""
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
        """If user accepts """
        friend_request = form.instance
        if 'accept_button' in self.request.POST:
            friend_request.status = 'accepted'
            friends_group, created = Group.objects.get_or_create(name=f'{self.request.user}_friends')
            sender_friends_group, created = Group.objects.get_or_create(name=f'{friend_request.sender}_friends')
            sender_friends_group.user_set.add(self.request.user)
            friends_group.user_set.add(friend_request.sender)
            self.request.user.friends.add(friend_request.sender)
        elif 'decline_button' in self.request.POST:
            friend_request.status = 'canceled'
        form.save()
        friend_request.delete()
        return redirect('user_detail', username=self.request.user.username)
    

class FriendRequestDelete(LoginRequiredMixin, DeleteView):
    """Delete friend invitation"""
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
    

# class RoomInvite(LoginRequiredMixin, CreateView):
#     """Send notification to private room creator's friends for join the room"""
#     model = RoomInvite
    
#     def get_object(self, request, *args, **kwargs):
#         room_id = self.kwargs['pk']
#         room = Room.objects.get(id=room_id)
#         return room

#     def get(self, *args, **kwargs):
#         logged_user = self.request.user
#         room = self.get_object()
#         pass