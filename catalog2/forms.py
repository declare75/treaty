from django import forms
from .models import Prepods, Subject

class PrepodForm(forms.ModelForm):
    class Meta:
        model = Prepods
        fields = ['subject', 'description']
        labels = {
            'subject': 'Предмет',
            'description': 'Описание',
        }
        subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)