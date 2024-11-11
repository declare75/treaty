from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import edit_prepod

urlpatterns = [
    path('', views.catalog2_home, name='catalog2_home'),
    path('success/', views.success_page, name='success_page'),
    path('add-prepod/', views.add_prepod, name='add_prepod'),
    path('user-prepods/', views.user_prepods, name='user_prepods'),
    path('edit-prepod/', edit_prepod, name='edit_prepod'),
    path('posts/', views.user_prepods, name='user_prepods'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
