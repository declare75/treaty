from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
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
        return f"{self.full_name} - {self.email}"

    def get_display_name(self):
        return f"{self.first_name} {self.last_name[0]}.{self.middle_name[0]}."

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_custom_user(sender, instance, created, **kwargs):
        if not instance.pk:
            instance.save()
