from typing import Any, Dict
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model

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
    """Show every room"""
    model = Room
    paginate_by = 20
    

class RoomDetails(DetailView):
    model = Room
    context_object_name = 'room'
    

class UserProfile(DetailView):
    model = User
    context_object_name = 'user'
