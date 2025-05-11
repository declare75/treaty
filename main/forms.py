
from django import forms
from .models import CustomUser


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'avatar',
            'birthday',
            'phone',
            'contact',
            'email',
            'last_name',
            'first_name',
            'middle_name',
        ]

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError('Фамилия обязательна.')
        return last_name

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('Имя обязательно.')
        return first_name
