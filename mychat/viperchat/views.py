from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView


class HomePage(View):
    """Start page view with links"""
    template_name = 'viperchat/base.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'welcome': 'Welcome to great chat',

        }
        return render(request, self.template_name, context)
    

class CreateRoom(CreateView):
    """This view is destined to create rooms"""
    pass
