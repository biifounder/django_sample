import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import live.routing  # This is the crucial line that connects to your app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_sample.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            live.routing.websocket_urlpatterns
        )
    ),
})
