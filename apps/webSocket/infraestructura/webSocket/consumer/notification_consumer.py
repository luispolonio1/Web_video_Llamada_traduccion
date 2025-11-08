import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.webSocket.dominio.puertos.mensajes_puerto import Socket

# 🔸 Diccionario global de usuarios conectados
connected_users = {}  # {"username": channel_name}


class NotificationConsumer(AsyncWebsocketConsumer, Socket):
    """
    WebSocket encargado de manejar notificaciones de llamadas:
    - call_request
    - call_accepted
    - call_rejected
    Hereda de Socket para mantener consistencia con la capa de aplicación.
    """

    async def connect(self):
        self.username = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else "Anónimo"
        )

        connected_users[self.username] = self.channel_name
        await self.accept()

        print(f"🔔 {self.username} conectado al socket de notificaciones.")

    async def disconnect(self, close_code):
        """Eliminar usuario al desconectarse"""
        if self.username in connected_users:
            del connected_users[self.username]
            print(f"🔕 {self.username} desconectado del socket de notificaciones.")

    async def receive(self, text_data=None, bytes_data=None):
        """Maneja los diferentes tipos de mensajes del frontend"""
        try:
            data = json.loads(text_data) if text_data else {}
        except Exception:
            data = {}

        msg_type = data.get("type")
        room_name = data.get("room_name")
        target_user = data.get("to")
        caller = data.get("from")

        # 🔹 Notificar solicitud de llamada
        if msg_type == "call_request":
            print(f"📞 Llamada de {self.username} hacia {target_user} (sala: {room_name})")

            if target_user and target_user in connected_users:
                await self.channel_layer.send(
                    connected_users[target_user],
                    {
                        "type": "notify_message",
                        "message": {
                            "type": "incoming_call",
                            "from": self.username,
                            "room_name": room_name,
                        },
                    },
                )
            else:
                await self.send(
                    text_data=json.dumps({
                        "type": "error",
                        "detail": f"El usuario '{target_user}' no está conectado."
                    })
                )

        # 🔹 Llamada aceptada
        elif msg_type == "call_accepted":
            print(f"✅ {self.username} aceptó la llamada de {caller}")
            if caller in connected_users:
                await self.channel_layer.send(
                    connected_users[caller],
                    {
                        "type": "notify_message",
                        "message": {
                            "type": "call_accepted",
                            "from": self.username,
                            "room_name": room_name,
                        },
                    },
                )

        # 🔹 Llamada rechazada
        elif msg_type == "call_rejected":
            print(f"❌ {self.username} rechazó la llamada de {caller}")
            if caller in connected_users:
                await self.channel_layer.send(
                    connected_users[caller],
                    {
                        "type": "notify_message",
                        "message": {
                            "type": "call_rejected",
                            "from": self.username,
                            "room_name": room_name,
                        },
                    },
                )

    async def notify_message(self, event):
        """Envía notificación directa a un usuario."""
        await self.send(text_data=json.dumps(event["message"]))

    # ----------------------------------------------------------------
    # 🔧 Implementaciones obligatorias de la interfaz Socket
    # ----------------------------------------------------------------
    async def send_message(self, message):
        """Implementación requerida por la clase Socket (no se usa aquí)."""
        await self.send(text_data=json.dumps(message))

    async def receive_message(self, data):
        """Implementación requerida por la clase Socket (no se usa aquí)."""
        print("📩 Mensaje recibido (interfaz Socket, no usado en notify):", data)