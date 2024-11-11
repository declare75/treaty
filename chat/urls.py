from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.chat_list_view, name="chat_list"),
    path('', views.chat_view, name='chats'),
    path("chat/<int:receiver_id>/", views.chat_view, name="chat_view"),
]