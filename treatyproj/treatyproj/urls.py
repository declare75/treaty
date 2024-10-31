from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.contrib import admin
from catalog2 import views




urlpatterns = [
    path('', include('main.urls')),
    path('catalog2/', include('catalog2.urls')),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('chats/', include('chat.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
