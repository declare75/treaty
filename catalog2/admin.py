from django.contrib import admin
from .models import Prepods, Subject
from django.utils.html import format_html


class PrepodsAdmin(admin.ModelAdmin):
    # Отображаем сгенерированное поле для ФИО, предмет, одобрение и дату создания
    list_display = ('get_title', 'get_subject', 'is_approved', 'created_at')
    actions = ['approve_selected', 'revoke_selected']

    def get_title(self, obj):
        # Формируем ФИО преподавателя из связанных полей пользователя
        return f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name}"

    get_title.short_description = 'ФИО преподавателя'

    def get_subject(self, obj):
        # Отображаем название предмета, связанного с объявлением
        return obj.subject.name if obj.subject else "Не указан"

    get_subject.short_description = 'Предмет'

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Объявления одобрены.")

    def revoke_selected(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Объявления отозваны.")

    approve_selected.short_description = "Одобрить выбранные объявления"
    revoke_selected.short_description = "Отозвать выбранные объявления"


# Регистрируем модель предметов, чтобы ими можно было управлять через админку
admin.site.register(Subject)
admin.site.register(Prepods, PrepodsAdmin)
