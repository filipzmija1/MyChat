from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Room

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
        return super().form_valid(form)
        
        
class RoomList(View):
    pass


class UserList(ListView):
    pass
