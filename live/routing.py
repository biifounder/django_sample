from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # This is the original, specific route that requires a room name.
    re_path(r'ws/quiz/(?P<room_name>\w+)/$', consumers.QuizConsumer.as_asgi()),
    
    # This is the new, non-specific route for the base URL.
    # It will catch any WebSocket connection to 'ws/quiz/'.
    re_path(r'ws/quiz/$', consumers.QuizConsumer.as_asgi()),
]