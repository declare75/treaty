from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import register_view, login_view, catalog2_home, edit_prepod

urlpatterns = [
    path('', views.catalog2_home, name='catalog2_home'),
    path('success/', views.success_page, name='success_page'),
    path('register/', register_view, name='register'),
    path('add-prepod/', views.add_prepod, name='add_prepod'),
    path('user-prepods/', views.user_prepods, name='user_prepods'),
    path('edit-prepod/', edit_prepod, name='edit_prepod'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
