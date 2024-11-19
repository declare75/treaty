from django.contrib.auth import get_user_model
from .models import CustomUser
from django.http import JsonResponse
import json
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

CustomUser = get_user_model()


def index(request):
    return render(request, 'main/index.html')


def catalog(request):
    return render(request, 'main/catalog.html')


def profile(request):
    return render(request, 'main/profile.html')


def help(request):
    return render(request, 'main/help.html')


@login_required
def profile_view(request):
    required_fields = []

    if not request.user.phone:
        required_fields.append('Телефон')
    if not request.user.birthday:
        required_fields.append('Дата рождения')
    if not request.user.contact:
        required_fields.append('Связь')

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, request.FILES, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            # Если все обязательные поля заполнены, показать сообщение об успешном сохранении
            if not required_fields:
                messages.success(request, 'Данные профиля успешно обновлены!')
            return redirect('profile')
    else:
        user_form = CustomUserForm(instance=request.user)

    # Передаем список незаполненных обязательных полей
    if required_fields:
        messages.warning(request, f'Пожалуйста, заполните следующие поля: {", ".join(required_fields)}.')

    return render(request, 'main/profile.html', {
        'user_form': user_form,
        'required_fields': required_fields
    })


def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Получаем данные с клиента
            last_name = data.get('last_name')
            first_name = data.get('first_name')
            middle_name = data.get('middle_name')
            email = data.get('email')
            password = data.get('password')

            # Проверка на существующего пользователя
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Пользователь с таким email уже существует.'})

            # Проверка, что все необходимые поля заполнены
            if not all([last_name, first_name, middle_name, email, password]):
                return JsonResponse({'success': False, 'message': 'Все поля обязательны для заполнения.'})

            # Создаем нового пользователя
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                username=email  # Используем email как username
            )
            user.save()

            # Авторизация пользователя после регистрации
            login(request, user)

            # Успешная регистрация
            return JsonResponse({
                'success': True,
                'message': 'Регистрация прошла успешно!',
                'redirect_url': '/profile/'  # Перенаправление после успешной регистрации
            })

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'message': 'Ошибка в формате запроса.'})

    return JsonResponse({'success': False, 'message': 'Некорректный запрос.'})


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Используем кастомную модель для аутентификации
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Неверные учетные данные'})
