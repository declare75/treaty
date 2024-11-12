from .models import Prepods, Subject
from .forms import PrepodForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

# Получаем кастомную модель пользователя
CustomUser = get_user_model()


def catalog2_home(request):
    if request.method == 'POST':
        form = PrepodForm(request.POST, request.FILES)
        if form.is_valid():
            # Добавляем проверку для сотрудников
            if not request.user.is_staff:
                return JsonResponse({'message': 'Только сотрудники могут добавлять объявления.'}, status=403)

            prepod = form.save(commit=False)
            prepod.is_approved = False  # Объявление идет на модерацию
            prepod.user = request.user  # Сохраняем пользователя, который создает объявление
            prepod.save()
            return JsonResponse({'message': 'Объявление успешно отправлено на модерацию!'})
        else:
            return JsonResponse({'message': 'Ошибка в отправленных данных.'}, status=400)

    # Получаем все предметы для отображения в форме
    subjects = Subject.objects.all()

    # Отображаем список одобренных объявлений
    catalog2 = Prepods.objects.filter(is_approved=True)
    form = PrepodForm()  # Форма для добавления нового объявления

    return render(request, 'catalog2/catalog2_home.html', {
        'catalog2': catalog2,
        'form': form,
        'subjects': subjects  # Передаем предметы в шаблон
    })

def success_page(request):
    return render(request, 'catalog2/success_page.html')

@login_required
def add_prepod(request):
    if not request.user.is_staff:
        return JsonResponse({'message': 'Только сотрудники могут добавлять объявления.'}, status=403)

    if request.method == 'POST':
        form = PrepodForm(request.POST, request.FILES)
        if form.is_valid():
            prepod = form.save(commit=False)
            prepod.user = request.user
            prepod.save()
            return redirect('catalog2_home')
        else:
            return JsonResponse({'message': 'Ошибка в форме'}, status=400)

    form = PrepodForm()
    return render(request, 'catalog2_home.html', {'form': form})

@login_required
def user_prepods(request):
    user_prepods = Prepods.objects.filter(user=request.user)
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
            return JsonResponse({'success': False, 'message': 'Ошибка в форме'}, status=400)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)

def get_subjects(request):
    subjects = Subject.objects.all()
    subjects_data = [{"id": subject.id, "name": subject.name} for subject in subjects]
    return JsonResponse({"subjects": subjects_data})
