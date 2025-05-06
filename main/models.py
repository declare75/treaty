from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from datetime import date
from django.utils import timezone
from django.db import transaction
from django.db.models import F


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        # Убедитесь, что 'username' не передается в `self.model`
        if 'username' in extra_fields:
            del extra_fields['username']  # Удаляем 'username', если оно передано
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

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
    is_teacher = models.BooleanField(default=False)  # Заменили is_active на is_teacher
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    rating = models.FloatField(default=0.0)
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    def transfer_balance(self, recipient, amount):

        if amount <= 0:
            raise ValueError("Сумма перевода должна быть положительной")

        if self.balance < amount:
            return False
        try:
            with transaction.atomic():
                # Списываем деньги с отправителя
                CustomUser.objects.filter(pk=self.pk).update(balance=F('balance') - amount)
                # Начисляем деньги получателю
                CustomUser.objects.filter(pk=recipient.pk).update(balance=F('balance') + amount)
                return True
        except Exception as e:
            raise Exception(f"Ошибка при переводе: {str(e)}")

    def calculate_rating(self):
        from catalog2.models import Review  # Импорт модели Review

        reviews = Review.objects.filter(teacher=self)
        if reviews.exists():
            self.rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        else:
            self.rating = 0.0
        self.save()

    def get_display_name(self):
        return f"{self.first_name} {self.last_name[0]}.{self.middle_name[0]}."

    def get_age(self):
        if self.birthday:
            today = date.today()
            age = today.year - self.birthday.year
            if today.month < self.birthday.month or (
                today.month == self.birthday.month and today.day < self.birthday.day
            ):
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
