from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Lesson
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils.dateparse import parse_duration
from datetime import timedelta

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
        return redirect("chat_list_view")

    # Фильтруем сообщения между текущим пользователем и получателем
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver) & ~Q(content__icontains="Для Вас назначено новое занятие!")) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by("timestamp")

    # Получаем все занятия для текущего пользователя и его чата с выбранным получателем
    lessons = Lesson.objects.filter(
        Q(teacher=request.user, student=receiver) |
        Q(teacher=receiver, student=request.user)
    ).order_by("date_time")

    # Считаем количество занятий между пользователями
    lessons_count = lessons.count()

    # Кнопки для начала/завершения занятия
    start_lesson_button = None
    end_lesson_button = None

    for lesson in lessons:
        if lesson.status == 'scheduled' and lesson.teacher == request.user:
            start_lesson_button = lesson  # Преподаватель может начать занятие
        elif lesson.status == 'in_progress' and lesson.teacher == request.user:
            end_lesson_button = lesson  # Преподаватель может завершить занятие


    if request.method == "POST":
        # Проверка на создание занятия
        if "schedule_lesson" in request.POST:
            if not request.user.is_staff:  # Проверяем, преподаватель ли пользователь
                return render(request, "main/chat_detail.html", {
                    "messages": messages,
                    "receiver": receiver,
                    "error": "Только преподаватели могут создавать занятия."
                })

            date_time = request.POST.get("date_time")
            duration = request.POST.get("duration")
            topic = request.POST.get("topic")

            try:
                # Преобразование строки в timedelta
                duration_obj = parse_duration(duration)
                if not duration_obj:  # Если parse_duration не справился
                    hours, minutes = map(int, duration.split(":"))
                    duration_obj = timedelta(hours=hours, minutes=minutes)

                # Находим второго участника чата (ученик)
                student = receiver if request.user != receiver else None

                if student is None:
                    return render(request, "main/chat_detail.html", {
                        "messages": messages,
                        "receiver": receiver,
                        "error": "Не удалось определить ученика."
                    })

                # Создаем занятие
                lesson = Lesson.objects.create(
                    date_time=date_time,
                    duration=duration_obj,
                    topic=topic,
                    teacher=request.user,
                    student=student,
                    status="pending",  # Статус "ожидает подтверждения"
                )


                # Отправляем сообщение в чат для подтверждения занятия
                Message.objects.create(
                    sender=request.user,
                    receiver=student,
                    content=(
                        f"<div class='contentzone'>"
                        f"<div class='newlessontext'>Для Вас назначено новое занятие!</div>"
                        f"<div class='newlessontext'>Тема: {lesson.topic}</div>"
                        f"<div class='newlessontext'>Дата: {lesson.date_time.replace('T', ' ').replace('-', '.')}</div>"
                        f"<div class='newlessontext'>Длительность: {lesson.duration}</div>"
                        f"<div class='approvepart'>Подтвердите участие:</div>"
                        f"<a href='{request.path}?confirm_lesson={lesson.id}' class='approvelesson'>Подтвердить </a>"
                        f"<a href='{request.path}?decline_lesson={lesson.id}' class='declinelesson'>Отказаться</a>"
                        f"</div>"
                    ),
                    timestamp=timezone.now(),
                )




            except (ValueError, AttributeError):
                return render(request, "main/chat_detail.html", {
                    "messages": messages,
                    "receiver": receiver,
                    "error": "Некорректная длительность."
                })

            return redirect("chat_view", receiver_id=receiver.id)

        # Обработка отправки сообщений
        content = request.POST.get("content")
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            image=image,
            video=video,
            timestamp=timezone.now(),
        )
        return redirect("chat_view", receiver_id=receiver.id)

    # Подтверждение или отклонение занятия
    confirm_lesson_id = request.GET.get("confirm_lesson")
    decline_lesson_id = request.GET.get("decline_lesson")

    if confirm_lesson_id:
        try:
            lesson = Lesson.objects.get(id=confirm_lesson_id)
            if lesson.student == request.user:
                lesson.status = 'scheduled'  # Изменяем статус на 'scheduled'
                lesson.save()
                # Отправляем сообщение, что занятие подтверждено
                Message.objects.create(
                    sender=request.user,
                    receiver=lesson.teacher,
                    content=f"<div class='newlessontext'>Занятие на тему {lesson.topic} подтверждено и запланировано</div>",
                    timestamp=timezone.now(),
                )
        except Lesson.DoesNotExist:
            pass

    if decline_lesson_id:
        try:
            lesson = Lesson.objects.get(id=decline_lesson_id)
            if lesson.student == request.user:
                lesson.status = 'declined'  # Если отклонить, то меняем статус на 'declined'
                lesson.save()
                # Отправляем сообщение, что занятие отклонено
                Message.objects.create(
                    sender=request.user,
                    receiver=lesson.teacher,
                    content=f"Занятие на тему '{lesson.topic}' отклонено.",
                    timestamp=timezone.now(),
                )
        except Lesson.DoesNotExist:
            pass

    if request.method == "GET" and "start_lesson" in request.GET:
        lesson_id = request.GET.get("start_lesson")
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            if lesson.teacher == request.user and lesson.status == 'scheduled':
                lesson.status = 'in_progress'
                lesson.save()

                # Получаем тему занятия, если она пустая, используем дефолтное значение
                topic = lesson.topic if lesson.topic else "Без темы"
                content = f"Занятие на тему '{topic}' началось."

                # Создаем сообщение с заданным content
                Message.objects.create(
                    sender=request.user,
                    receiver=lesson.student,
                    content=content,  # Убедитесь, что content всегда передается
                    timestamp=timezone.now(),
                )
        except Lesson.DoesNotExist:
            pass

    # Обработка нажатия кнопки "Завершить занятие"
    if request.method == "GET" and "end_lesson" in request.GET:
        lesson_id = request.GET.get("end_lesson")
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            if lesson.teacher == request.user and lesson.status == 'in_progress':
                lesson.status = 'completed'
                lesson.save()

                # Используем тему занятия или дефолтное значение
                content = f"Занятие на тему '{lesson.topic or 'Без темы'}' завершено."

                Message.objects.create(
                    sender=request.user,
                    receiver=lesson.student,
                    content=content,  # Убедитесь, что content всегда передается
                    timestamp=timezone.now(),
                )
        except Lesson.DoesNotExist:
            pass

    return render(request, "main/chat_detail.html", {
        "messages": messages,
        "receiver": receiver,
        "lessons": lessons,  # Передаем список всех занятий
        "lessons_count": lessons_count,  # Передаем количество занятий
        "start_lesson_button": start_lesson_button,
        "end_lesson_button": end_lesson_button
    })

@login_required
def videocall(request):
    return render(request, 'main/videocall.html', {'name': request.chat.chat_user.get_display_name + " " + request.user.last_name})
