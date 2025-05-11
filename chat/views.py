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
from datetime import timedelta, datetime
import random
from decimal import Decimal
from .models import Message, Lesson, CustomUser
from django.contrib.auth import get_user_model
from django.core.cache import cache
from asgiref.sync import sync_to_async
import asyncio
import json
from django.utils import formats
import os


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
    if request.method == "POST" and ('content' in request.POST or 'file' in request.FILES):
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
    file = request.FILES.get("file")  # Изменено с image и video на file

    if not (content or file):
        return JsonResponse({"success": False, "error": "Сообщение пустое"}, status=400)

    # Опциональная валидация типов файлов
    if file:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm', 'ogg', 'txt', 'docx', 'doc', 'pdf']
        extension = os.path.splitext(file.name)[1][1:].lower()  # Извлекаем расширение без точки
        if extension not in allowed_extensions:
            return JsonResponse({"success": False, "error": "Недопустимый тип файла"}, status=400)
        if file and file.size > 10 * 1024 * 1024:  # 10MB
            return JsonResponse({"success": False, "error": "Файл слишком большой"}, status=400)

    try:
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content or '',  # Если content пустой, сохраняем пустую строку
            file=file,  # Сохраняем файл в поле file
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
                "file": message.file.url if message.file else None,  # Возвращаем URL файла
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



# Получаем кастомную модель пользователя
CustomUser = get_user_model()

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

    # Очищаем price от лишних символов (например, "₽")
    try:
        price = price.replace(" ₽", "").strip()  # Удаляем "₽" и пробелы
        price = Decimal(price)
    except (ValueError, AttributeError):
        return JsonResponse({"success": False, "error": "Введите корректную стоимость"}, status=400)

    if price <= 0:
        return JsonResponse({"success": False, "error": "Стоимость должна быть больше нуля"}, status=400)

    try:
        # Преобразуем date_time в объект datetime
        # Формат для datetime-local: 'YYYY-MM-DDThh:mm'
        date_time_obj = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')
        # Устанавливаем временную зону
        date_time_obj = timezone.make_aware(date_time_obj, timezone.get_current_timezone())

        # Обрабатываем duration
        duration_obj = parse_duration(duration)
        if not duration_obj:
            # parse_duration может не распознать "0:12:03", поэтому обрабатываем вручную
            time_parts = duration.split(":")
            if len(time_parts) != 2:  # Ожидаем формат "HH:MM"
                raise ValueError("Некорректный формат длительности. Ожидается HH:MM")
            hours, minutes = map(int, time_parts)
            duration_obj = timedelta(hours=hours, minutes=minutes)

        lesson = Lesson.objects.create(
            date_time=date_time_obj,  # Передаем объект datetime
            duration=duration_obj,
            topic=topic,
            teacher=request.user,
            student=receiver,
            status="pending",
            price=price,
        )

        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=(
                f"<div class='contentzone'>"
                f"<div class='newlessontext'>Для Вас назначено новое занятие!</div>"
                f"<div class='newlessontext'>Тема: {lesson.topic}</div>"
                f"<div class='newlessontext'>Дата: {lesson.date_time.strftime('%Y.%m.%d %H:%M')}</div>"
                f"<div class='newlessontext'>Длительность: {lesson.duration}</div>"
                f"<div class='newlessontext'>Стоимость: {lesson.price} ₽</div>"
                f"<div class='approvepart'>Подтвердите участие:</div>"
                f"<a href='{reverse('confirm_lesson', args=[receiver.id, lesson.id])}' class='approvelesson'>Подтвердить </a>"
                f"<a href='{reverse('decline_lesson', args=[receiver.id, lesson.id])}' class='declinelesson'>Отказаться</a>"
                f"</div>"
            ),
            timestamp=timezone.now(),
        )

        return JsonResponse({
            "success": True,
            "message": {
                "id": message.id,
                "sender": message.sender.email,
                "sender_name": message.sender.get_display_name(),
                "content": message.content,
                "timestamp": message.timestamp.strftime('%d %B %H:%M'),
            },
            "lesson": {
                "id": lesson.id,
                "topic": lesson.topic,
                "date_time": lesson.date_time.strftime('%d %B %H:%M'),
                "status": lesson.status,
                "teacher": lesson.teacher.email,
                "student": lesson.student.email,
            }
        })
    except (ValueError, AttributeError) as e:
        return JsonResponse({"success": False, "error": f"Ошибка: {str(e)}"}, status=400)


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
        lesson.call_link = link
        lesson.save()

        topic = lesson.topic if lesson.topic else "Без темы"
        content = (
            f"Занятие на тему '{topic}' началось. "
            f'<div><a href="{link}" target="_blank" style="padding: 10px 20px; background-color: #466ee5; '
            f'border: none; border-radius: 4px; color: white; text-decoration: none; display: inline-block; '
            f'text-align: center;">Перейти к занятию</a></div>'
        )
        Message.objects.create(
            sender=request.user,
            receiver=lesson.student,
            content=content,
            timestamp=timezone.now(),
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": True,
                "lesson": {
                    "id": lesson.id,
                    "status": lesson.status,
                    "topic": lesson.topic,
                    "date_time": formats.date_format(lesson.date_time, "j F, H:i"),
                    "teacher": lesson.teacher.email,
                    "student": lesson.student.email,
                    "updated_at": lesson.updated_at.isoformat(),
                },
                "room_id": room_id
            })
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

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": True,
                "lesson": {
                    "id": lesson.id,
                    "status": lesson.status,
                    "topic": lesson.topic,
                    "date_time": formats.date_format(lesson.date_time, "j F, H:i"),
                    "teacher": lesson.teacher.email,
                    "student": lesson.student.email,
                    "updated_at": lesson.updated_at.isoformat(),
                }
            })
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
    ).order_by('timestamp').select_related('sender')

    return [{
        'id': msg.id,
        'sender': msg.sender.email,
        'sender_name': msg.sender.get_display_name(),
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%d %B %H:%M'),
        'file': msg.file.url if msg.file else None,  # Заменили image и video на file
    } for msg in messages]


@login_required
async def sse_messages(request, receiver_id):
    await check_auth(request.user)

    async def event_stream():
        last_message_id = request.GET.get('last_id', 0)
        last_updated_at = request.GET.get('last_updated_at', None)
        receiver = await get_receiver(receiver_id)

        while True:
            # Получаем новые сообщения
            messages_data = await get_new_messages(last_message_id, request.user, receiver)
            for data in messages_data:
                yield f"data: {json.dumps({'type': 'message', 'data': data})}\n\n"
                last_message_id = data['id']

            # Получаем обновления уроков
            lessons_data = await get_lesson_updates(last_updated_at, request.user, receiver)
            for data in lessons_data:
                yield f"data: {json.dumps({'type': 'lesson', 'data': data})}\n\n"
                last_updated_at = data['updated_at']

            await asyncio.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response


@sync_to_async
def get_lesson_updates(last_updated_at, user, receiver):
    from zoneinfo import ZoneInfo
    try:
        last_updated_at = timezone.datetime.fromisoformat(
            last_updated_at) if last_updated_at else timezone.datetime.min.replace(tzinfo=ZoneInfo('UTC'))
    except ValueError:
        last_updated_at = timezone.datetime.min.replace(tzinfo=ZoneInfo('UTC'))

    lessons = Lesson.objects.filter(
        Q(teacher=user, student=receiver) | Q(teacher=receiver, student=user),
        updated_at__gt=last_updated_at
    ).exclude(status__in=['pending', 'declined']).order_by("date_time").select_related('teacher', 'student')

    return [{
        'id': lesson.id,
        'topic': lesson.topic,
        'status': lesson.status,
        'date_time': formats.date_format(lesson.date_time, "j F, H:i"),
        'teacher': lesson.teacher.email,
        'student': lesson.student.email,
        'updated_at': lesson.updated_at.isoformat(),
    } for lesson in lessons]
