from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.chat_list_view, name='chat_list_view'),
    path('chat/<int:receiver_id>/', views.chat_view, name='chat_view'),
    path('chat/<int:receiver_id>/messages/', views.get_messages, name='get_messages'),
    path('chat/<int:receiver_id>/send/', views.send_message, name='send_message'),
    path('chat/<int:receiver_id>/schedule/', views.schedule_lesson, name='schedule_lesson'),
    path('chat/<int:receiver_id>/confirm/<int:lesson_id>/', views.confirm_lesson, name='confirm_lesson'),
    path('chat/<int:receiver_id>/decline/<int:lesson_id>/', views.decline_lesson, name='decline_lesson'),
    path('chat/<int:receiver_id>/start/<int:lesson_id>/', views.start_lesson, name='start_lesson'),
    path('chat/<int:receiver_id>/end/<int:lesson_id>/', views.end_lesson, name='end_lesson'),
]