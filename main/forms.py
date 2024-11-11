# forms.py
from django import forms
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar', 'birthday', 'phone', 'contact', 'email', 'full_name']
