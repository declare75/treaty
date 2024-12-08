from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic', 'date_time', 'duration', 'student', 'teacher')
    list_filter = ('date_time', 'teacher', 'student')
    search_fields = ('topic', 'teacher__email', 'student__email')
