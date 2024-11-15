from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Настройка отображения полей в списке
    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}"
    full_name.admin_order_field = 'last_name'  # Устанавливаем сортировку по фамилии
    full_name.short_description = 'ФИО'  # Заголовок столбца в админке

    list_display = ('email', 'full_name', 'birthday', 'phone', 'contact', 'is_active', 'is_staff')

    # Поля, которые можно редактировать в списке
    list_filter = ('is_staff', 'is_active')

    # Поля для поиска
    search_fields = ('email', 'first_name', 'last_name', 'middle_name')

    # Поля, которые будут показываться при добавлении и редактировании пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Email и пароль
        ('Personal info', {'fields': ('first_name', 'last_name', 'middle_name', 'birthday', 'phone', 'contact', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Настройки для изменения списка полей при добавлении
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'first_name', 'last_name', 'middle_name', 'birthday', 'phone', 'contact', 'is_active', 'is_staff'),
        }),
    )

    # Убираем поля, которые не существуют в модели CustomUser
    filter_horizontal = []
    ordering = ['email']


# Регистрируем модель CustomUser
admin.site.register(CustomUser, CustomUserAdmin)
