import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.webSocket.dominio.puertos.mensajes_puerto import Socket
from apps.webSocket.aplicacion.servicios.servicio_de_videollamada import (
    VideoCallService,
)
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


class VideoCallConsumer(AsyncWebsocketConsumer, Socket):
    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data) if text_data else {}
        except Exception:
            data = {}
        await self.receive_message(data)


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
        elif msg_type == "prediccion_final":
            print("Llegó")
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            user_text = (
                (data or {}).get("traduccion") if isinstance(data, dict) else data
            )

            if not isinstance(user_text, str) or not user_text.strip():
                await self.send(
                    text_data=json.dumps(
                        {
                            "kind": "error",
                            "detail": "Falta campo 'traduccion' como string",
                        }
                    )
                )
                return

            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un traductor que convierte palabras o frases provenientes de ASL al español. "
                            "Sigue estas reglas: "
                            "respeta los pronombres"
                            "1. Si solo hay una palabra, Si es un sustantivo, solo agrega artículo si es necesario (ej: 'casa' -> 'la casa'). "
                            "2. No inventes contexto"
                            "3. Si hay varias palabras, ordénalas y genera UNA sola oración corta, natural y correctamente conjugada. "
                            "4. Sigue este ejemplo si solo ves un adjetivo 'triste' -> 'me siento triste' "
                            "No quiero que des explicaciones de nada"
                        ),
                    },
                    {"role": "user", "content": user_text},
                ],
                temperature=0.2,
            )

            traduccion = chat_completion.choices[0].message.content.strip()
            print(f"Traduccion: {traduccion}")

            await self.send(
                text_data=json.dumps(
                    {
                        "kind": "ack",
                        "detail": "Predicción recibida",
                        "traduccion": traduccion,
                        "user": self.username,
                    }
                )
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_message",
                    "message": {"type": "prediccion", "text": traduccion},
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
