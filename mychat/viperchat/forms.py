from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm

from .models import Room, ServerPermissionSettings


class UserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class UserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class SignUpForm(SignupForm):
    first_name = forms.CharField(
        max_length=64,
        label='First name',
        widget=forms.TextInput(attrs={'placeholder': 'Name'})
    )
    last_name = forms.CharField(
        max_length=64,
        label='Surname',
        widget=forms.TextInput(attrs={'placeholder': 'Surname'})
    )
    username = forms.CharField(
        max_length=150,
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )

    def signup(self, request, user):
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

    def save(self, request):
        user = super(SignUpForm, self).save(request)
        return user
    

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)


class SearchForm(forms.Form):
    CHOICES = (
        ('room', 'room'),
        ('user', 'user'),
    )
    search = forms.CharField(min_length=1, required=False)
    search_by = forms.ChoiceField(choices=CHOICES)


class RoomManagementForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['description', 'is_private']


class ServerPermissionsForm(forms.ModelForm):
    class Meta:
        model = ServerPermissionSettings
        fields = ['moderators_delete_messages', 'moderators_delete_user', 'moderators_send_invitation', 'members_send_invitation']


class SendMessageForm(forms.Form):
    message = forms.CharField(max_length=255)

