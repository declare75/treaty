from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q


@login_required
def chat_list_view(request):
    # Получаем уникальные чаты пользователя
    user = request.user
    existing_chats = User.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).distinct()

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            receiver = User.objects.get(email=email)
            return redirect("chat_view", receiver_id=receiver.id)
        except User.DoesNotExist:
            # Обработка ошибки, если пользователь с указанным email не найден
            return render(request, "main/chat_list.html", {"error": "Пользователь не найден", "existing_chats": existing_chats})

    return render(request, "main/chat_list.html", {"existing_chats": existing_chats})


@login_required
def chat_view(request, receiver_id):
    receiver = User.objects.get(id=receiver_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("content")
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        Message.objects.create(sender=request.user, receiver=receiver, content=content, image=image, video=video, timestamp=timezone.now())
        return redirect("chat_view", receiver_id=receiver.id)

    return render(request, "main/chat_detail.html", {"messages": messages, "receiver": receiver})
