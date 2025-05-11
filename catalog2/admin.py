from django.contrib import admin
from .models import Announcement, Subject, Review
from django.utils.html import format_html

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = ('get_title', 'get_subject', 'is_approved', 'created_at')
    actions = ['approve_selected', 'revoke_selected']

    def get_title(self, obj):

        return f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name}"

    get_title.short_description = 'ФИО преподавателя'

    def get_subject(self, obj):

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
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'reviewer',
        'teacher',
        'rating',
        'created_at',
    )
    list_filter = ('rating', 'created_at')
    search_fields = (
        'reviewerusername',
        'teacherusername',
        'text',
    )  # Поля для поиска
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)