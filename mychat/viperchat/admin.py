from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Room
from .forms import UserCreationForm, UserChangeForm


User = get_user_model()


class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = [
        'email',
        'username',
        'is_superuser'
    ]

admin.site.register(User, UserAdmin)
admin.site.register(Room)