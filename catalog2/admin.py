# admin.py
from django.contrib import admin
from .models import Prepods
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class PrepodsAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'is_approved', 'created_at')
    actions = ['approve_selected', 'revoke_selected']

    def approve_selected(self, request, queryset):

        queryset.update(is_approved=True)
        self.message_user(request, "Объявления одобрены.")

    def revoke_selected(self, request, queryset):

        queryset.update(is_approved=False)
        self.message_user(request, "Объявления отозваны.")

    approve_selected.short_description = "Одобрить выбранные объявления"
    revoke_selected.short_description = "Отозвать выбранные объявления"

admin.site.register(Prepods, PrepodsAdmin)
