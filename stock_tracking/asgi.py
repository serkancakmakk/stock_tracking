import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path

from stock.routing import websocket_urlpatterns
from stock import consumers  # WebSocket yönlendirme yapılandırmanızı içeren dosya

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_tracking.settings')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_tracking.settings')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_tracking.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]