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
from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import SingleObjectMixin

from .models import Room, Notification, FriendRequest, RoomInvite, Message, PermissionSettings
from .forms import ResetPasswordForm, SearchForm, RoomManagementForm, SendMessageForm
from .permissions import *


User = get_user_model()


class HomePage(View):
    """Start page view with links"""
    template_name = 'viperchat/base.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'welcome': 'Welcome to great chat',
        }
        return render(request, self.template_name, context)
    

class CreateRoom(LoginRequiredMixin, CreateView):
    """Create room and groups with permissions. Creates 3 groups (Room Masters, Members and Moderators). 
    By default all members can invite"""
    model = Room
    fields = ['name', 'description', 'is_private']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        permission_settings = PermissionSettings.objects.create()
        form.instance.permission_settings = permission_settings
        room = form.save()
        room.users.add(self.request.user)

        moderators_group, status = Group.objects.get_or_create(name=f'{room.name}_mods')  # Create moderator group
        members_group, created = Group.objects.get_or_create(name=f'{room.name}_members')    # Create members group
        room_masters, is_created = Group.objects.get_or_create(name=f'{room.name}_masters')

        moderators_group.user_set.add(self.request.user)      
        members_group.user_set.add(self.request.user)
        room_masters.user_set.add(self.request.user)

        add_delete_message_permission(moderators_group)
        add_delete_user_from_group_permission(moderators_group)
        add_send_invitation_permission(moderators_group)

        add_send_invitation_permission(members_group)

        add_delete_message_permission(room_masters)
        add_delete_user_from_group_permission(room_masters)
        add_send_invitation_permission(room_masters)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('room_detail', kwargs={'pk': self.object.pk})
        

class DeleteMessage(LoginRequiredMixin, DeleteView):
    """logged user or room moderator can delete message in room"""
    model = Message

    def get_object(self, *args, **kwargs):
        message_id = self.kwargs['pk']
        message = Message.objects.get(id=message_id)
        room = message.room
        moderators_group = Group.objects.get(name=f'{room.name}_mods')
        room_masters = Group.objects.get(name=f'{room.name}_masters')
        logged_user = self.request.user
        delete_message_permission = Permission.objects.get(codename='delete_message_from_room')
        if logged_user in room_masters.user_set.all() or logged_user == message.author:     # Check if user belongs to room_masters group
            return message
        elif delete_message_permission in moderators_group.permissions.all() and logged_user in moderators_group.user_set.all():    # Check if delete permission and logged user are in moderate group
            return message
        else:
            raise PermissionDenied
        
    def get_success_url(self):
        room = self.get_object().room
        return reverse('room_detail', kwargs={'pk': room.pk})


class RoomList(ListView):
    """Shows every room"""
    model = Room
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        public_rooms = Room.objects.filter(is_private=False)
        context['room_list'] = public_rooms
        return context


class JoinRoom(LoginRequiredMixin, UpdateView):
    """Allows user to join to public room"""
    model = Room

    def get_object(self, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(pk=room_id)
        return room
    
    def get(self, request, *args, **kwargs):
        room = self.get_object()
        member_group = Group.objects.get(name=f'{room.name}_members')
        if room.is_private == False:
            room.users.add(self.request.user)
            member_group.user_set.add(self.request.user)
            room.save()
            return redirect(reverse('room_detail', kwargs={'pk': room.pk}))
        else:
            raise PermissionDenied
    

class RoomDetail(LoginRequiredMixin, FormMixin, DetailView):
    """Shows room details and gives posibility to write message in chatroom"""
    model = Room
    context_object_name = 'room'
    form_class = SendMessageForm

    def get_object(self, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        logged_user = self.request.user
        if room.is_private == True and logged_user in room.users.all():
            return room
        elif room.is_private == True and logged_user not in room.users.all():
            raise PermissionDenied
        else:
            return room
        
    def get_context_data(self,  *args, **kwargs):
        context = super().get_context_data(**kwargs)
        logged_user = self.request.user
        logged_user_friends = logged_user.friends.all()
        room_masters = Group.objects.get(name=f'{self.get_object().name}_masters')
        room_moderators = Group.objects.get(name=f'{self.get_object().name}_mods')
        delete_message_permission = Permission.objects.get(codename='delete_message_from_room')
        context['friends'] = logged_user_friends
        context['messages'] = Message.objects.filter(room=self.get_object())
        context['masters'] = room_masters.user_set.all()
        context['form'] = SendMessageForm() 
        if delete_message_permission in room_moderators.permissions.all(): # Check if moderators have permission to display delete message button
            context['moderators'] = room_moderators.user_set.all()
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            room = self.get_object()
            author = self.request.user
            message = form.cleaned_data['message']
            Message.objects.create(room=room, author=author, content=message)
            return redirect(reverse('room_detail', kwargs={'pk': self.get_object().pk}))
        else:
            return redirect(reverse('room_detail', kwargs={'pk': self.get_object().pk}))

    
class RoomManagement(LoginRequiredMixin, UpdateView):
    """Moderators delete messages, send invites, delete users in room"""
    model = Room
    form_class = RoomManagementForm
    template_name = 'viperchat/room_management.html'

    def get_object(self, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        room_masters = Group.objects.get(name=f'{room.name}_masters')
        if self.request.user in room_masters.user_set.all():
            return room
        else:
            raise PermissionDenied

    def get_initial(self):
        initial = {}
        permission_settings = self.get_object().permission_settings
        initial['delete_messages'] = permission_settings.delete_messages
        initial['delete_user'] = permission_settings.delete_user
        initial['moderators_send_invitation'] = permission_settings.moderators_send_invitation
        initial['members_send_invitation'] = permission_settings.members_send_invitation
        return self.initial.copy()
        
    def form_valid(self, form):
        moderator_delete_messages_permission = form.cleaned_data['delete_messages']
        moderator_delete_user_permission = form.cleaned_data['delete_user']
        moderators_send_invite_permission = form.cleaned_data['moderators_send_invitation']
        members_send_invite_permission = form.cleaned_data['members_send_invitation']
        moderator_group = Group.objects.get(name=f'{self.get_object().name}_mods')
        member_group = Group.objects.get(name=f'{self.get_object().name}_members')
        permission_settings = self.get_object().permission_settings
        
        set_permission(moderator_delete_messages_permission, moderator_group, add_delete_message_permission, remove_delete_message_permission)
        set_permission(moderator_delete_user_permission, moderator_group, add_delete_user_from_group_permission, remove_user_from_group_permission)
        set_permission(moderators_send_invite_permission, moderator_group, add_send_invitation_permission, remove_send_invitation_permission)
        set_permission(members_send_invite_permission, member_group, add_send_invitation_permission, remove_send_invitation_permission)

        form.save()
        return redirect(reverse('room_detail', kwargs={'pk': self.get_object().pk}))
        

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
        user_rooms = Room.objects.filter(creator=self.request.user)
        context['friend_request'] = friend_request
        context['friend_request_mirror'] = friend_request_mirror
        context['user_rooms'] = user_rooms
        if self.request.user in self.get_object().friends.all():
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
    """View destined to delete friend from friendlist"""
    def get(self, request, *args, **kwargs):
        user_username = self.kwargs['username']
        user_to_remove = User.objects.get(username=user_username)
        logged_user = self.request.user
        if not logged_user.friends.filter(username=user_to_remove.username).exists():
            raise PermissionDenied
        else:
            logged_user.friends.remove(user_to_remove)
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
        

class FriendRequestUpdate(LoginRequiredMixin, UpdateView):
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
        friend_request = form.instance
        if 'accept_button' in self.request.POST:
            friend_request.status = 'accepted'
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