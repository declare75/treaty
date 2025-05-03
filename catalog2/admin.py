from django.contrib import admin
from .models import Announcement, Subject, Review
from django.utils.html import format_html

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
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

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Предполагается, что у Subject есть поле name
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'reviewer',
        'teacher',
        'rating',
        'created_at',
    )  # Поля, отображаемые в списке
    list_filter = ('rating', 'created_at')  # Возможность фильтрации
    search_fields = (
        'reviewerusername',
        'teacherusername',
        'text',
    )  # Поля для поиска
    ordering = ('-created_at',)  # Сортировка по умолчанию (новые отзывы сверху)
    readonly_fields = ('created_at',)