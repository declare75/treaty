from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog', views.catalog, name='catalog'),
    path('profile', views.profile, name='profile'),
    path('help', views.help, name='help'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
