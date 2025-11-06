import json
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.webSocket.dominio.puertos.mensajes_puerto import Socket


class NotificationConsumer(AsyncWebsocketConsumer, Socket):
    """
    WebSocket encargado de manejar notificaciones de llamadas:
    - call_request
    - call_accepted
    - call_rejected
    ✅ Usa Redis para manejar los usuarios conectados.
    """

    async def connect(self):
        user = self.scope.get("user")
        self.username = user.username if user and user.is_authenticated else "Anónimo"

        # 🔹 Conectarse a Redis
        self.redis = await redis.from_url("redis://127.0.0.1:6379", decode_responses=True)



        # Guardar al usuario conectado (username → channel_name)
        await self.redis.hset("connected_users", self.username, self.channel_name)

        await self.accept()
        print(f"🔔 {self.username} conectado al socket de notificaciones.")

    async def disconnect(self, close_code):
        """Eliminar usuario de Redis al desconectarse."""
        if hasattr(self, "redis"):
            await self.redis.hdel("connected_users", self.username)
            await self.redis.close()
        print(f"🔕 {self.username} desconectado del socket de notificaciones.")

    async def receive(self, text_data=None, bytes_data=None):
        """Maneja los diferentes tipos de mensajes del frontend."""
        data = json.loads(text_data or "{}")
        msg_type = data.get("type")
        room_name = data.get("room_name")
        target_user = data.get("to")
        caller = self.username

        # 📞 Llamada solicitada
        if msg_type == "call_request":
            target_channel = await self.redis.hget("connected_users", target_user)

            if target_channel:
                await self.channel_layer.send(
                    target_channel,
                    {
                        "type": "notify_message",
                        "message": {
                            "type": "incoming_call",
                            "from": caller,
                            "room_name": room_name,
                        },
                    },
                )
                await self.send(text_data=json.dumps({
                    "type": "call_sent",
                    "to": target_user,
                    "room_name": room_name,
                    "status": "waiting_response",
                }))
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "detail": f"El usuario '{target_user}' no está conectado."
                }))

        # ✅ Llamada aceptada
        elif msg_type == "call_accepted":
            from_user = data.get("from")
            caller_channel = await self.redis.hget("connected_users", from_user)
            if caller_channel:
                await self.channel_layer.send(
                    caller_channel,
                    {
                        "type": "notify_message",
                        "message": {
                            "type": "call_accepted",
                            "from": caller,
                            "room_name": room_name,
                        },
                    },
                )

        # ❌ Llamada rechazada
        elif msg_type == "call_rejected":
            from_user = data.get("from")
            caller_channel = await self.redis.hget("connected_users", from_user)
            if caller_channel:
                await self.channel_layer.send(
                    caller_channel,
                    {
                        "type": "notify_message",
                        "message": {
                            "type": "call_rejected",
                            "from": caller,
                            "room_name": room_name,
                        },
                    },
                )

    async def notify_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    # Implementaciones requeridas por Socket
    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    async def receive_message(self, data):
        print("📩 Mensaje recibido (interfaz Socket, no usado en notify):", data)
