from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, required=True, label="ФИО")  # Новое поле ФИО

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birthday', 'phone', 'contact', 'full_name']
