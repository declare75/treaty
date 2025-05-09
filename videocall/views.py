from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from chat.models import Lesson


@login_required
def main_view(request):
    # Извлекаем roomID из параметров запроса
    room_id = request.GET.get('roomID', '')

    if not room_id:
        raise Http404("Room ID not provided")

    # Проверяем, существует ли занятие с таким roomID в call_link
    try:
        Lesson.objects.get(call_link__contains=room_id)
    except Lesson.DoesNotExist:
        raise Http404("Lesson with this room ID does not exist")

    # Если занятие существует, рендерим страницу видеозвонка
    context = {
        'room_id': room_id,
        'user': request.user,
    }
    return render(request, 'videocall/main.html', context)