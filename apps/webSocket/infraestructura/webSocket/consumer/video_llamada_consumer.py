import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.webSocket.dominio.puertos.mensajes_puerto import Socket
from apps.webSocket.aplicacion.servicios.servicio_de_videollamada import VideoCallService


class VideoCallConsumer(AsyncWebsocketConsumer, Socket):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.username = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else "Anónimo"
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        service = VideoCallService(self)
        await service.notificar_union(self.username)

    async def disconnect(self, close_code):
        service = VideoCallService(self)
        await service.notificar_salida(self.username)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_message(self, message):
        """Implementación concreta del envío de mensajes al cliente."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signal_message",
                "message": message,
                "sender_channel": self.channel_name,
            },
        )

    async def receive_message(self, data):
        """Procesa los mensajes recibidos desde los clientes."""
        msg_type = data.get("type")

        if msg_type in ["prediccion", "translation"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_message",
                    "message": data,
                    "sender_channel": self.channel_name,
                },
            )
        elif msg_type in ["call_request", "call_accepted", "call_rejected"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",
                    "message": {
                        "type": msg_type,
                        "from": self.username,
                    },
                    "sender_channel": self.channel_name,
                },
            )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",
                    "message": data,
                    "sender_channel": self.channel_name,
                },
            )

    async def signal_message(self, event):
        """Envía mensajes de señalización a otros clientes del grupo."""
        if self.channel_name != event.get("sender_channel"):
            await self.send(text_data=json.dumps(event["message"]))

    async def broadcast_message(self, event):
        """Envía mensajes de difusión a todos los demás usuarios."""
        if self.channel_name != event.get("sender_channel"):
            await self.send(
                text_data=json.dumps(
                    {"type": "broadcast_message", "message": event["message"]}
                )
            )
