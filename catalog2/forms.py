from django import forms
from .models import Announcement, Subject, Review


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['subject', 'description']
        labels = {
            'subject': 'Предмет',
            'description': 'Описание',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Ваш отзыв...', 'rows': 3}),
            'rating': forms.HiddenInput(),  # Скрытое поле для рейтинга
        }
