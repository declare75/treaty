from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):

    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}"

    full_name.admin_order_field = 'last_name'
    full_name.short_description = 'ФИО'

    list_display = (
        'email',
        'full_name',
        'birthday',
        'phone',
        'contact',
        'is_teacher',
        'is_staff',
        'balance',
    )


    list_filter = ('is_staff', 'is_teacher')


    search_fields = ('email', 'first_name', 'last_name', 'middle_name')


    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal info',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'middle_name',
                    'birthday',
                    'phone',
                    'contact',
                    'avatar',
                    'balance',
                )
            },
        ),
        ('Permissions', {'fields': ('is_teacher', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )


    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'middle_name',
                    'birthday',
                    'phone',
                    'contact',
                    'is_teacher',
                    'is_staff',
                    'balance',
                ),
            },
        ),
    )


    filter_horizontal = []
    ordering = ['email']



admin.site.register(CustomUser, CustomUserAdmin)
