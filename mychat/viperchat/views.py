from typing import Any, Dict, Optional
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.contrib import messages

from .models import Room, Notification, FriendRequest, RoomInvite
from .forms import ResetPasswordForm, SearchForm


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
    """This view is destined to create rooms"""
    model = Room
    fields = ['name', 'description', 'is_private']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        room = form.save()
        room.users.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('room_detail', kwargs={'pk': self.object.pk})
        

class RoomList(ListView):
    """Shows every room"""
    model = Room
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        public_rooms = Room.objects.filter(is_private=False)
        context['room_list'] = public_rooms
        return context
    

class RoomDetails(DetailView):
    """Shows room details"""
    model = Room
    context_object_name = 'room'

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
        context['friends'] = logged_user_friends
        return context
        


class UserOwnRooms(LoginRequiredMixin, ListView):
    """Display user own rooms"""
    model = Room
    context_object_name = "user_rooms"
    template_name = 'viperchat/user_own_rooms.html'

    def get_queryset(self):
        logged_user = self.request.user
        rooms = Room.objects.filter(users=logged_user)
        return rooms


class UserProfile(DetailView):
    """Shows user profile"""
    model = User
    template_name = 'viperchat/user_profile.html'
    context_object_name = 'user'

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
        return context
    

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
    

class PrivateRoomInvite(LoginRequiredMixin, CreateView):
    """Send notification to private room creator's friends for join the room"""
    model = RoomInvite
    
    def get_object(self, request, *args, **kwargs):
        room_id = self.kwargs['pk']
        room = Room.objects.get(id=room_id)
        if room.creator != self.request.user:
            raise PermissionDenied
        else:
            return Room
    