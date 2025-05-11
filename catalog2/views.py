from .models import Announcement, Subject
from .forms import AnnouncementForm, ReviewForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from chat.models import Lesson
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


CustomUser = get_user_model()


def teacher_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_teacher:
            return JsonResponse({'message': 'Только сотрудники могут выполнять это действие.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def catalog2_home(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.is_approved = False
            announcement.user = request.user
            announcement.save()
            return JsonResponse({'message': 'Объявление успешно отправлено на модерацию!'})
        else:
            return JsonResponse({'message': 'Ошибка в отправленных данных.'}, status=400)

    if not request.user.is_authenticated and request.GET.get('action') == 'contact':
        messages.warning(request, 'Чтобы связаться, необходимо войти в аккаунт.')
        return redirect('catalog2_home')


    subjects_cache_key = 'all_subjects'
    subjects = cache.get(subjects_cache_key)
    if not subjects:
        subjects = Subject.objects.all()
        cache.set(subjects_cache_key, subjects, 60 * 60)


    catalog2 = Announcement.objects.filter(is_approved=True).select_related('user')
    paginator = Paginator(catalog2, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = ReviewForm()

    return render(request, 'catalog2/catalog2_home.html', {
        'catalog2': page_obj,
        'form': form,
        'subjects': subjects,
    })

def success_page(request):
    return render(request, 'catalog2/success_page.html')

@login_required
@teacher_required
def add_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.save()
            return redirect('catalog2_home')
        else:
            return JsonResponse({'message': 'Ошибка в форме'}, status=400)

    form = AnnouncementForm()
    return render(request, 'catalog2/catalog2_home.html', {'form': form})

@login_required
def user_announcements(request):
    user_announcements = Announcement.objects.filter(user=request.user)
    return render(request, 'catalog2/posts.html', {'announcements': user_announcements})

@login_required
def edit_announcement(request):
    if request.method == 'POST':
        data = request.POST
        announcement_id = data.get('id')
        announcement = get_object_or_404(Announcement, id=announcement_id)

        form = AnnouncementForm(data, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Объявление успешно обновлено!'})
        else:
            return JsonResponse({'success': False, 'message': 'Ошибка в форме'}, status=400)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)

@cache_page(60 * 60)
def get_subjects(request):
    subjects = Subject.objects.all()
    subjects_data = [{"id": subject.id, "name": subject.name} for subject in subjects]
    return JsonResponse({"subjects": subjects_data})

@login_required
def add_review(request, teacher_id):
    teacher = get_object_or_404(CustomUser, id=teacher_id, is_staff=True)


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
            return redirect("catalog2_home")
    else:
        form = ReviewForm()

    return render(request, "catalog2/add_review.html", {"form": form, "teacher": teacher})