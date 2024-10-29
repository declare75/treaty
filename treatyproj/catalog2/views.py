from .models import Prepods
from .forms import PrepodForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json

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

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Пользователь с таким email уже существует'})

        user = User.objects.create_user(username=email, email=email, password=password)
        return JsonResponse({'success': True})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Неверные учетные данные'})

@login_required
def add_prepod(request):
    if request.method == 'POST':
        form = PrepodForm(request.POST, request.FILES)
        if form.is_valid():
            prepod = form.save(commit=False)
            prepod.user = request.user
            prepod.save()
            return JsonResponse({'message': 'Объявление добавлено успешно!'})
        else:
            return JsonResponse({'message': 'Ошибка в форме'}, status=400)
    return JsonResponse({'message': 'Неверный метод запроса'}, status=405)

@login_required
def user_prepods(request):
    user_prepods = Prepods.objects.filter(user=request.user)
    return render(request, 'catalog2/posts.html', {'prepods': user_prepods})

login_required
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
