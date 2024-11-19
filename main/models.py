from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from datetime import date


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        # Убедитесь, что 'username' не передается в `self.model`
        if 'username' in extra_fields:
            del extra_fields['username']  # Удаляем 'username' если оно передано
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    contact = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=150, blank=False)  # Фамилия
    first_name = models.CharField(max_length=150, blank=False)  # Имя
    middle_name = models.CharField(max_length=150, blank=False)  # Отчество
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    def get_display_name(self):
        return f"{self.first_name} {self.last_name[0]}.{self.middle_name[0]}."

    def get_age(self):
        if self.birthday:
            today = date.today()
            age = today.year - self.birthday.year
            if today.month < self.birthday.month or (
                    today.month == self.birthday.month and today.day < self.birthday.day):
                age -= 1

            if age % 10 == 1 and age % 100 != 11:
                age_str = f"{age} год"
            elif 2 <= age % 10 <= 4 and not (12 <= age % 100 <= 14):
                age_str = f"{age} года"
            else:
                age_str = f"{age} лет"

            return age_str
        return None

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_custom_user(sender, instance, created, **kwargs):
        if not instance.pk:
            instance.save()
