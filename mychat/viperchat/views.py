from typing import Any, Dict, Optional
from django.db import models
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from .models import Room


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
        return f'/rooms/{self.object.pk}'
        
class RoomList(ListView):
    """Shows every room"""
    model = Room
    paginate_by = 20
    

class RoomDetails(DetailView):
    """Shows room details"""
    model = Room
    context_object_name = 'room'
    

class UserProfile(DetailView):
    """Shows user profile"""
    model = User
    template_name = 'viperchat/user_profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        return user
    

class UserProfileEdit(UpdateView):
    """This view is destined to change user data"""
    mdoel = User
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