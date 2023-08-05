from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm

from .models import Room, ServerPermissionSettings, Server


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
        fields = [
                  'masters_create_room', 'masters_can_edit_rooms', 'masters_can_edit_users_group', 'masters_send_invitation_to_group', 'masters_delete_user', 'masters_can_see_private_rooms',
                  'masters_delete_messages', 'masters_send_messages', 'moderators_create_room', 'moderators_delete_messages',
                  'moderators_delete_user', 'moderators_can_edit_rooms', 'moderators_send_invitation_to_group', 'moderators_send_messages','moderators_can_see_private_rooms', 
                  'members_create_room', 'members_delete_messages', 'members_send_invitation_to_group', 'members_send_messages',
                  'members_can_see_private_rooms'
                  ]


class SendMessageForm(forms.Form):
    message = forms.CharField(max_length=255)


class ServerEditForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['description', 'is_private']


