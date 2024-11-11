from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth import get_user_model  # Импортируем get_user_model()
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse

# Получаем кастомную модель пользователя
CustomUser = get_user_model()


@login_required
def chat_list_view(request):
    user = request.user

    # Получаем уникальные чаты пользователя, используя кастомную модель
    existing_chats = CustomUser.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).distinct()

    chat_data = []
    for chat_user in existing_chats:
        # Получаем последнее сообщение для каждого чата
        last_message = Message.objects.filter(
            Q(sender=user, receiver=chat_user) | Q(sender=chat_user, receiver=user)
        ).order_by("-timestamp").first()

        chat_data.append({
            'chat_user': chat_user,
            'last_message': last_message
        })

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            # Используем кастомную модель для получения пользователя по email
            receiver = CustomUser.objects.get(email=email)
            return JsonResponse({"redirect_url": reverse("chat_view", args=[receiver.id])})
        except CustomUser.DoesNotExist:
            # Проверка, является ли запрос AJAX-запросом
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"error": "Пользователь с таким email не найден."})
            else:
                return render(request, "main/chat_list.html", {"existing_chats": existing_chats})

    return render(request, "main/chat_list.html", {"chat_data": chat_data})


@login_required
def chat_view(request, receiver_id):
    try:
        receiver = CustomUser.objects.get(id=receiver_id)
    except CustomUser.DoesNotExist:
        return redirect("chat_list_view")  # Если пользователь не найден, перенаправляем на список чатов

    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("content")
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        Message.objects.create(sender=request.user, receiver=receiver, content=content, image=image, video=video,
                               timestamp=timezone.now())
        return redirect("chat_view", receiver_id=receiver.id)

    return render(request, "main/chat_detail.html", {"messages": messages, "receiver": receiver})
