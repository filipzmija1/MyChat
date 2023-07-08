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