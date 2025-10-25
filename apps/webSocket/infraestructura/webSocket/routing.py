from django.urls import re_path
from apps.webSocket.infraestructura.webSocket.consumer.video_llamada_consumer import VideoCallConsumer

websocket_urlpatterns = [
    re_path(r"ws/call/(?P<room_name>\w+)/$", VideoCallConsumer.as_asgi()),
]
