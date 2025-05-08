from django.urls import path
from . import views

app_name = 'videocall'  # 🛠️ ADDED: Define app_name for namespace

urlpatterns = [
    path('', views.main_view, name='main'),
]
