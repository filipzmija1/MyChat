from django.shortcuts import render
from django.views import View


class HomePage(View):
    template_name = 'viperchat/base.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'welcome': 'Welcome to great chat',

        }
        return render(request, self.template_name, context)
    