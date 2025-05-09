from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="message_images/", null=True, blank=True)
    video = models.FileField(upload_to="message_videos/", null=True, blank=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    class Meta:
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp']),
            models.Index(fields=['receiver', 'sender', 'timestamp']),
            models.Index(fields=['id']),
        ]


class Lesson(models.Model):
    date_time = models.DateTimeField()
    duration = models.DurationField()
    topic = models.CharField(max_length=255)
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="lessons_as_student"
    )
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="lessons_as_teacher"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает подтверждения'),
            ('scheduled', 'Запланировано'),
            ('in_progress', 'В процессе'),
            ('completed', 'Завершено'),
            ('declined', 'Отклонено'),
        ],
        default='pending',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Lesson on {self.topic} at {self.date_time.strftime('%Y-%m-%d %H:%M')}"

    @staticmethod
    def has_completed_lesson(student, teacher):
        return Lesson.objects.filter(
            student=student, teacher=teacher, status="completed"
        )
