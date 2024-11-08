from django import forms
from .models import Prepods
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class PrepodForm(forms.ModelForm):
    class Meta:
        model = Prepods
        fields = ['title', 'subject', 'description', 'age', 'date', 'rating', 'avatar', 'contact_link']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email / Username")
    password = forms.CharField(widget=forms.PasswordInput)