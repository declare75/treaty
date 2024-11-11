from .models import Prepods
from .forms import PrepodForm
from django.contrib.auth import get_user_model  # Используем get_user_model()
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

import json

# Получаем кастомную модель пользователя
CustomUser = get_user_model()


def catalog2_home(request):
    if request.method == 'POST':
        form = PrepodForm(request.POST, request.FILES)
        if form.is_valid():
            prepod = form.save(commit=False)
            prepod.is_approved = False
            prepod.save()
            return JsonResponse({'message': 'Объявление успешно отправлено на модерацию!'})
        else:
            return JsonResponse({'message': 'Ошибка в отправленных данных.'}, status=400)

    catalog2 = Prepods.objects.filter(is_approved=True)
    return render(request, 'catalog2/catalog2_home.html', {'catalog2': catalog2})

def success_page(request):
    return render(request, 'catalog2/success_page.html')





@login_required
def add_prepod(request):
    if request.method == 'POST':
        form = PrepodForm(request.POST, request.FILES)
        if form.is_valid():
            prepod = form.save(commit=False)
            prepod.user = request.user  # Здесь используем CustomUser, так как это текущий пользователь
            prepod.save()
            return JsonResponse({'message': 'Объявление добавлено успешно!'})
        else:
            return JsonResponse({'message': 'Ошибка в форме'}, status=400)
    return JsonResponse({'message': 'Неверный метод запроса'}, status=405)

@login_required
def user_prepods(request):
    user_prepods = Prepods.objects.filter(user=request.user)  # Здесь также работаем с CustomUser
    return render(request, 'catalog2/posts.html', {'prepods': user_prepods})

@login_required
def edit_prepod(request):
    if request.method == 'POST':
        data = request.POST
        prepod_id = data.get('id')
        prepod = get_object_or_404(Prepods, id=prepod_id)

        form = PrepodForm(data, request.FILES, instance=prepod)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Объявление успешно обновлено!'})
        else:
            print(form.errors)
            return JsonResponse({'success': False, 'message': 'Ошибка в форме'}, status=400)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)
