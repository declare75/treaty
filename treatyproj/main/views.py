
from django.contrib.auth.models import User
from .models import Profile
from django.http import JsonResponse
import json


def index(request):
    return render(request, 'main/index.html')


def catalog(request):
    return render(request, 'main/catalog.html')


def profile(request):
    return render(request, 'main/profile.html')


def help(request):
    return render(request, 'main/help.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserForm, ProfileForm


@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Сохраняем изменения пользователя и профиля
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'main/profile.html', {'user_form': user_form, 'profile_form': profile_form})




def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('name', '').split()
        email = data.get('email')
        password = data.get('password')

        if len(full_name) >= 2:  # Проверка на наличие хотя бы Имени и Фамилии
            user = User.objects.create_user(
                username=email,  # или другое уникальное значение
                email=email,
                password=password,
                first_name=full_name[0],
                last_name=" ".join(full_name[1:])
            )
            Profile.objects.create(user=user)  # Создаем пустой профиль при регистрации

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Введите полное ФИО.'})

    return JsonResponse({'success': False, 'message': 'Некорректный запрос.'})
