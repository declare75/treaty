import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import videocall.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatyproj.settings')
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            videocall.routing.websocket_urlpatterns
        )
    )
})
