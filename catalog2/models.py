from django.contrib.auth import get_user_model
from django.db import models

# Используем кастомную модель пользователя
CustomUser = get_user_model()

class Prepods(models.Model):
    title = models.CharField('ФИО', max_length=50)
    subject = models.CharField('Предмет', max_length=35)
    description = models.CharField('Описание', max_length=250)
    age = models.CharField('Возраст', max_length=8)
    date = models.DateTimeField('Дата публикации')
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=2)
    avatar = models.ImageField(upload_to='img/', verbose_name='Аватар')
    created_at = models.DateTimeField(auto_now=True)
    contact_link = models.URLField('Ссылка для связи', blank=True, null=True)
    is_approved = models.BooleanField('Одобрено', default=False)

    # Здесь связываем модель с CustomUser
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='prepods')

    def revoke(self):
        self.is_approved = False
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'объявление'
        verbose_name_plural = 'Каталоги'
