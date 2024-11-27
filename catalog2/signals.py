from django.db.models.signals import post_save
from django.dispatch import receiver
from catalog2.models import Review
from main.models import CustomUser

@receiver(post_save, sender=Review)
def update_teacher_rating(sender, instance, **kwargs):
    teacher = instance.teacher
    teacher.calculate_rating()
