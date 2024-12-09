import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing  # Убедитесь, что путь к chat.routing правильный

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatyproj.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns  # Используется правильный путь
            )
        ),
    }
)
