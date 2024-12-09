from .models import Prepods, Subject
from .forms import PrepodForm, ReviewForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from chat.models import Lesson
from django.contrib import messages

# Получаем кастомную модель пользователя
CustomUser = get_user_model()

# Функция-декоратор для проверки is_staff
def staff_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({'message': 'Только сотрудники могут выполнять это действие.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def catalog2_home(request):
    if request.method == 'POST':
        form = PrepodForm(request.POST, request.FILES)
        if form.is_valid():
            prepod = form.save(commit=False)
            prepod.is_approved = False
            prepod.user = request.user
            prepod.save()
            return JsonResponse({'message': 'Объявление успешно отправлено на модерацию!'})
        else:
            return JsonResponse({'message': 'Ошибка в отправленных данных.'}, status=400)

    if not request.user.is_authenticated and request.GET.get('action') == 'contact':
        messages.warning(request, 'Чтобы связаться, необходимо войти в аккаунт.')
        return redirect('catalog2_home')

    subjects = Subject.objects.all()
    catalog2 = Prepods.objects.filter(is_approved=True).select_related('user')
    form = ReviewForm()

    return render(request, 'catalog2/catalog2_home.html', {
        'catalog2': catalog2,
        'form': form,
        'subjects': subjects,
    })


def success_page(request):
    return render(request, 'catalog2/success_page.html')


@login_required
@staff_required
def add_prepod(request):
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
    return render(request, 'catalog2/catalog2_home.html', {'form': form})


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


@login_required
def add_review(request, teacher_id):
    teacher = get_object_or_404(CustomUser, id=teacher_id, is_staff=True)

    # Проверяем наличие завершенного занятия
    if not Lesson.has_completed_lesson(student=request.user, teacher=teacher):
        messages.warning(request, 'Вы можете оставить отзыв только после завершенного занятия с этим преподавателем.')
        return redirect('catalog2_home')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.teacher = teacher
            review.save()
            return redirect("catalog2_home")  # Перенаправляем на главную страницу каталога
    else:
        form = ReviewForm()

    return render(request, "catalog2/add_review.html", {"form": form, "teacher": teacher})
