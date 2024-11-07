from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile
from django.http import JsonResponse
import json
from django.contrib.auth import logout as auth_logout
from django.contrib import messages



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
    required_fields = []

    # Проверка обязательных полей
    if not request.user.profile.phone:
        required_fields.append('Телефон')
    if not request.user.profile.birthday:
        required_fields.append('Дата рождения')
    if not request.user.profile.contact:
        required_fields.append('Связь')

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Если поля были заполнены, можно отправить сообщение
            if not required_fields:
                messages.success(request, 'Данные профиля успешно обновлены!')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    # Передаем список незаполненных обязательных полей
    if required_fields:
        messages.warning(request, f'Пожалуйста, заполните следующие поля: {", ".join(required_fields)}.')

    return render(request, 'main/profile.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'required_fields': required_fields})




def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        full_name = data.get('name', '').split()
        email = data.get('email')
        password = data.get('password')

        if len(full_name) >= 2:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name[0],
                last_name=" ".join(full_name[1:])
            )
            Profile.objects.create(user=user)


            login(request, user)

            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Некорректный запрос.'})
