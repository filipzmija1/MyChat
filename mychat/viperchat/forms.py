from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username']

class SignUpForm(SignupForm):

    first_name = forms.CharField(
        max_length=64,
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    last_name = forms.CharField(
        max_length=64,
        label='Surname',
        widget=forms.TextInput(attrs={'placeholder': 'Surname'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')