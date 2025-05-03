from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

# Используем кастомную модель пользователя
CustomUser = get_user_model()


class Subject(models.Model):
    name = models.CharField('Название предмета', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Announcement(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL, null=True, verbose_name='Предмет'
    )
    description = models.CharField('Описание', max_length=250)
    created_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField('Одобрено', default=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='prepods',
    )

    def revoke(self):
        self.is_approved = False
        self.save()

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.middle_name}"

    class Meta:
        verbose_name = 'объявление'
        verbose_name_plural = 'Каталоги'


class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )  # Кто оставил отзыв
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )  # Преподаватель, которому оставили отзыв
    text = models.TextField()  # Текст отзыва
    created_at = models.DateTimeField(auto_now_add=True)  # Время создания
    rating = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.reviewer} -> {self.teacher} ({self.rating})"
