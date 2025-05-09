from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.utils.dateparse import parse_duration
from django.contrib import messages
from django.db import transaction
from datetime import timedelta
import random
from decimal import Decimal
from .models import Message, Lesson, CustomUser
from django.contrib.auth import get_user_model
from django.core.cache import cache
from asgiref.sync import sync_to_async
import asyncio
import json

# Получаем кастомную модель пользователя
CustomUser = get_user_model()

def generate_room_link(request, lesson_id):
    while True:
        room_id = random.randint(1000, 9999)
        if not cache.get(f"room:{room_id}"):  # Проверяем, не занята ли комната
            cache.set(f"room:{room_id}", True, timeout=3600)  # Резервируем на 1 час
            break
    link = f"{request.scheme}://{request.get_host()}/videocall/?roomID={room_id}"
    return room_id, link

def chat_list_view(request):
    if not request.user.is_authenticated:
        messages.warning(
            request,
            'Чтобы увидеть данную страницу, необходимо авторизоваться.',
        )
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        return redirect('home')
    user = request.user

    existing_chats = CustomUser.objects.filter(
        Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
    ).distinct()

    chat_data = []
    for chat_user in existing_chats:
        last_message = (
            Message.objects.filter(
                Q(sender=user, receiver=chat_user) | Q(sender=chat_user, receiver=user)
            )
            .order_by("-timestamp")
            .first()
        )
        chat_data.append({'chat_user': chat_user, 'last_message': last_message})

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            receiver = CustomUser.objects.get(email=email)
            return JsonResponse(
                {"redirect_url": reverse("chat_view", args=[receiver.id])}
            )
        except CustomUser.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"error": "Пользователь с таким email не найден."})
            else:
                return render(
                    request,
                    "main/chat_list.html",
                    {"existing_chats": existing_chats},
                )

    return render(request, "main/chat_list.html", {"chat_data": chat_data})

@login_required
def chat_view(request, receiver_id):
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    # Фильтруем сообщения между текущим пользователем и получателем
    messages = Message.objects.filter(
        (
            Q(sender=request.user)
            & Q(receiver=receiver)
            & ~Q(content__icontains="Для Вас назначено новое занятие!")
        )
        | (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by("timestamp")

    # Получаем ID последнего сообщения
    last_message_id = messages.last().id if messages.exists() else 0

    # Получаем уроки
    lessons = Lesson.objects.filter(
        Q(teacher=request.user, student=receiver) | Q(teacher=receiver, student=request.user)
    ).order_by("date_time")

    lessons_count = lessons.count()

    # Кнопки для начала/завершения занятия
    start_lesson_button = None
    end_lesson_button = None
    for lesson in lessons:
        if lesson.status == 'scheduled' and lesson.teacher == request.user:
            start_lesson_button = lesson
        elif lesson.status == 'in_progress' and lesson.teacher == request.user:
            end_lesson_button = lesson

    # Обработка отправки сообщений через AJAX
    if request.method == "POST" and ('content' in request.POST or 'image' in request.FILES or 'video' in request.FILES):
        return send_message(request, receiver_id)

    return render(
        request,
        "main/chat_detail.html",
        {
            "messages": messages,
            "receiver": receiver,
            "lessons": lessons,
            "lessons_count": lessons_count,
            "start_lesson_button": start_lesson_button,
            "end_lesson_button": end_lesson_button,
            "last_message_id": last_message_id,
        },
    )

@login_required
def send_message(request, receiver_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Метод не разрешен"}, status=405)

    receiver = get_object_or_404(CustomUser, id=receiver_id)
    content = request.POST.get("content")
    image = request.FILES.get("image")
    video = request.FILES.get("video")

    if not (content or image or video):
        return JsonResponse({"success": False, "error": "Сообщение пустое"}, status=400)

    try:
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            image=image,
            video=video,
            timestamp=timezone.now(),
        )
        # Возвращаем данные о новом сообщении для немедленного отображения
        return JsonResponse({
            "success": True,
            "message": {
                "id": message.id,
                "sender": message.sender.email,
                "sender_name": message.sender.get_display_name(),
                "content": message.content,
                "timestamp": message.timestamp.strftime('%d %B %H:%M'),
                "image": message.image.url if message.image else None,
                "video": message.video.url if message.video else None,
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def schedule_lesson(request, receiver_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Метод не разрешен"}, status=405)

    if not request.user.is_teacher:
        return JsonResponse({"success": False, "error": "Только преподаватели могут создавать занятия"}, status=403)

    receiver = get_object_or_404(CustomUser, id=receiver_id)
    date_time = request.POST.get("date_time")
    duration = request.POST.get("duration")
    topic = request.POST.get("topic")
    price = request.POST.get("price")

    try:
        price = Decimal(price)
    except:
        return JsonResponse({"success": False, "error": "Введите корректную стоимость"}, status=400)

    if price <= 0:
        return JsonResponse({"success": False, "error": "Стоимость должна быть больше нуля"}, status=400)

    try:
        duration_obj = parse_duration(duration)
        if not duration_obj:
            hours, minutes = map(int, duration.split(":"))
            duration_obj = timedelta(hours=hours, minutes=minutes)

        lesson = Lesson.objects.create(
            date_time=date_time,
            duration=duration_obj,
            topic=topic,
            teacher=request.user,
            student=receiver,
            status="pending",
            price=price,
        )

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=(
                f"<div class='contentzone'>"
                f"<div class='newlessontext'>Для Вас назначено новое занятие!</div>"
                f"<div class='newlessontext'>Тема: {lesson.topic}</div>"
                f"<div class='newlessontext'>Дата: {lesson.date_time.replace('T', ' ').replace('-', '.')}</div>"
                f"<div class='newlessontext'>Длительность: {lesson.duration}</div>"
                f"<div class='newlessontext'>Стоимость: {lesson.price} ₽</div>"
                f"<div class='approvepart'>Подтвердите участие:</div>"
                f"<a href='{reverse('confirm_lesson', args=[receiver.id, lesson.id])}' class='approvelesson'>Подтвердить </a>"
                f"<a href='{reverse('decline_lesson', args=[receiver.id, lesson.id])}' class='declinelesson'>Отказаться</a>"
                f"</div>"
            ),
            timestamp=timezone.now(),
        )

        return redirect('chat_view', receiver_id=receiver.id)
    except (ValueError, AttributeError) as e:
        return JsonResponse({"success": False, "error": "Некорректная длительность или данные"}, status=400)

@login_required
def confirm_lesson(request, receiver_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.student != request.user:
        return JsonResponse({"success": False, "error": "Вы не можете подтвердить это занятие"}, status=403)

    try:
        with transaction.atomic():
            if lesson.student.balance < lesson.price:
                from urllib.parse import urlencode
                base_url = reverse('chat_view', kwargs={'receiver_id': lesson.teacher.id})
                query_string = urlencode({'error': 'balance'})
                return redirect(f'{base_url}?{query_string}')

            lesson.status = 'scheduled'
            lesson.save()

            success = lesson.student.transfer_balance(lesson.teacher, lesson.price)
            if not success:
                return JsonResponse({"success": False, "error": "Ошибка при переводе средств"}, status=500)

            Message.objects.create(
                sender=request.user,
                receiver=lesson.teacher,
                content=f"<div class='newlessontext'>Занятие на тему {lesson.topic} подтверждено и запланировано</div>",
                timestamp=timezone.now(),
            )
        return redirect('chat_view', receiver_id=lesson.teacher.id)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def decline_lesson(request, receiver_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.student != request.user:
        return JsonResponse({"success": False, "error": "Вы не можете отклонить это занятие"}, status=403)

    try:
        lesson.status = 'declined'
        lesson.save()
        Message.objects.create(
            sender=request.user,
            receiver=lesson.teacher,
            content=f"Занятие на тему '{lesson.topic}' отклонено.",
            timestamp=timezone.now(),
        )
        return redirect('chat_view', receiver_id=lesson.teacher.id)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def start_lesson(request, receiver_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.teacher != request.user or lesson.status != 'scheduled':
        return JsonResponse({"success": False, "error": "Вы не можете начать это занятие"}, status=403)

    try:
        lesson.status = 'in_progress'
        room_id, link = generate_room_link(request, lesson.id)
        lesson.call_link = link  # Сохраняем сгенерированную ссылку в модель
        lesson.save()

        topic = lesson.topic if lesson.topic else "Без темы"
        content = f"""
        Занятие на тему '{topic}' началось. 
        <div>
            <a href='{link}' target='_blank' style='padding: 10px 20px; background-color: #466ee5; border: none; border-radius: 4px; color: white; text-decoration: none; display: inline-block; text-align: center;'>
                Перейти к занятию
            </a>
        </div>"""

        Message.objects.create(
            sender=request.user,
            receiver=lesson.student,
            content=content,
            timestamp=timezone.now(),
        )

        return HttpResponseRedirect(reverse('videocall:main') + f'?roomID={room_id}')
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def end_lesson(request, receiver_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.teacher != request.user or lesson.status != 'in_progress':
        return JsonResponse({"success": False, "error": "Вы не можете завершить это занятие"}, status=403)

    try:
        lesson.status = 'completed'
        lesson.call_link = None
        lesson.save()

        content = f"Занятие на тему '{lesson.topic or 'Без темы'}' завершено."
        Message.objects.create(
            sender=request.user,
            receiver=lesson.student,
            content=content,
            timestamp=timezone.now(),
        )
        return redirect('chat_view', receiver_id=receiver_id)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@sync_to_async
def check_auth(user):
    if not user.is_authenticated:
        raise PermissionDenied("User is not authenticated")


@sync_to_async
def get_receiver(receiver_id):
    return get_object_or_404(CustomUser, id=receiver_id)


@sync_to_async
def get_new_messages(last_id, user, receiver):
    messages = Message.objects.filter(
        (
                Q(sender=user, receiver=receiver) |
                Q(sender=receiver, receiver=user)
        ),
        id__gt=last_id
    ).order_by('timestamp').select_related('sender')  # Оптимизация: подгружаем sender

    # Формируем данные в синхронном контексте
    return [{
        'id': msg.id,
        'sender': msg.sender.email,
        'sender_name': msg.sender.get_display_name(),
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%d %B %H:%M'),
        'image': msg.image.url if msg.image else None,
        'video': msg.video.url if msg.video else None,
    } for msg in messages]


@login_required
async def sse_messages(request, receiver_id):
    # Проверяем аутентификацию асинхронно
    await check_auth(request.user)

    async def event_stream():
        last_id = request.GET.get('last_id', 0)
        receiver = await get_receiver(receiver_id)

        while True:
            messages_data = await get_new_messages(last_id, request.user, receiver)

            for data in messages_data:
                yield f"data: {json.dumps(data)}\n\n"
                last_id = data['id']

            await asyncio.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response
