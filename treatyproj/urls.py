from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('main.urls')),
    path('catalog2/', include('catalog2.urls')),
    path('secret/admin/', admin.site.urls),
    path('chats/', include('chat.urls')),
    path('videocall/', include('videocall.urls', namespace='videocall')),
    path(
        'favicon.ico',
        RedirectView.as_view(url='/static/main/img/t.svg', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
