from django import forms
from .models import Prepods, Subject, Review

class PrepodForm(forms.ModelForm):
    class Meta:
        model = Prepods
        fields = ['subject', 'description']
        labels = {
            'subject': 'Предмет',
            'description': 'Описание',
        }
        subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Ваш отзыв...', 'rows': 3}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }