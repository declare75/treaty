from django import forms
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['date_time', 'duration', 'topic']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duration': forms.TextInput(attrs={'placeholder': 'Введите длительность в формате: HH:MM:SS'}),
            'topic': forms.TextInput(attrs={'placeholder': 'Введите тему занятия'}),
        }
