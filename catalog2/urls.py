from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.catalog2_home, name='catalog2_home'),
    path('success/', views.success_page, name='success_page'),
    path('add-prepod/', views.add_prepod, name='add_prepod'),
    # path('edit-prepod/', views.edit_prepod, name='edit_prepod'),
    # path('posts/', views.user_prepods, name='user_prepods'),
    path('get-subjects/', views.get_subjects, name='get_subjects'),
    path('get-subjects/', views.get_subjects, name='get_subjects'),
    path('add_review/<int:teacher_id>/', views.add_review, name='add_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
