from typing import Any, Dict, Optional
from django.db import models
from django.db.models import Q
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.contrib import messages

from .models import Room
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


class AddFriend(LoginRequiredMixin, View):
    """View destined to add friends"""
    def get(self, request, *args, **kwargs):
        user_username = self.kwargs['username']
        user = User.objects.get(username=user_username)
        logged_user = self.request.user
        if logged_user.friends.filter(username=user.username).exists() or logged_user == user:
            raise PermissionDenied
        else:
            logged_user.friends.add(user)
            logged_user.save()
            return redirect(reverse('user_detail', kwargs={'username': logged_user.username}))


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
                    Q(name__startswith=search_value))
            if search_by == 'user':
                search_result = User.objects.filter(
                    Q(username__icontains=search_value) | 
                    Q(username__startswith=search_value))
        return render(self.request, 'viperchat/search_form.html', self.get_context_data(form=form, search_result=search_result))
    

class DeleteFriend(LoginRequiredMixin, View):
    """View destined to delete friend from friendlist"""
    def get(self, request, *args, **kwargs):
        user_username = self.kwargs['username']
        user = User.objects.get(username=user_username)
        logged_user = self.request.user
        if not logged_user.friends.filter(username=user.username).exists():
            raise PermissionDenied
        else:
            pass