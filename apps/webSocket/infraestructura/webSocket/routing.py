from django.urls import re_path, path
from apps.webSocket.infraestructura.webSocket.consumer.video_llamada_consumer import VideoCallConsumer
from apps.webSocket.infraestructura.webSocket.consumer.notification_consumer import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/call/(?P<room_name>\w+)/$", VideoCallConsumer.as_asgi()),
    path("ws/notify/", NotificationConsumer.as_asgi()),
]
