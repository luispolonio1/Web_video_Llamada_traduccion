import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.webSocket.dominio.puertos.mensajes_puerto import Socket
from apps.webSocket.aplicacion.servicios.servicio_de_videollamada import VideoCallService
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Mapa de usuarios conectados (username -> channel_name)
connected_users = {}


class VideoCallConsumer(AsyncWebsocketConsumer, Socket):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.username = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else "Anónimo"
        )

        connected_users[self.username] = self.channel_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        service = VideoCallService(self)
        await service.notificar_union(self.username)

    async def disconnect(self, close_code):
        service = VideoCallService(self)
        await service.notificar_salida(self.username)

        if self.username in connected_users:
            del connected_users[self.username]

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data) if text_data else {}
        except Exception:
            data = {}

        await self.receive_message(data)

    # ------------- API Mensajería -------------
    async def send_message(self, message):
        """Reenvía señalización o mensajes al grupo."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signal_message",
                "message": message,
                "sender_channel": self.channel_name,
                "user": self.username,
            },
        )

    async def receive_message(self, data):
        msg_type = data.get("type")

        # ---- Señalización WebRTC básica ----
        if msg_type in ["offer", "answer", "ice"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signal_message",
                    "message": data,
                    "sender_channel": self.channel_name,
                },
            )
            return

        # ---- Voz -> señas (solo texto). El receptor construye la playlist vía HTTP ----
        if msg_type == "voice_to_sign":
            text = (data.get("text") or "").strip()
            if not text:
                await self.send(
                    text_data=json.dumps({"kind": "error", "detail": "texto vacío"})
                )
                return

            payload = {
                "type": "broadcast_message",
                "message": {  # 👇 importante: solo texto, NO regresa al emisor
                    "type": "voice_to_sign",
                    "text": text,
                    "user": self.username,
                },
                "sender_channel": self.channel_name,
            }
            await self.channel_layer.group_send(self.room_group_name, payload)
            await self.send(text_data=json.dumps(payload))
            return

        # ---- Predicción/Traducción final (tu flujo existente con Groq) ----
        if msg_type == "prediccion_final":
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            user_text = data.get("traduccion")

            if not isinstance(user_text, str) or not user_text.strip():
                await self.send(
                    text_data=json.dumps(
                        {"kind": "error", "detail": "Falta campo 'traduccion' como string"}
                    )
                )
                return

            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un traductor que convierte frases provenientes de ASL al español natural. "
                            "Sigue estas reglas: "
                            "1. Si solo hay una palabra y es un sustantivo, agrega artículo si es necesario (ej: 'casa' → 'la casa'). "
                            "2. No inventes contexto. "
                            "3. Si hay varias palabras, ordénalas y genera una oración corta natural y conjugada. "
                            "4. Si solo hay un adjetivo (ej: 'triste'), genera algo como 'me siento triste'. "
                            "5. No expliques nada adicional."
                        ),
                    },
                    {"role": "user", "content": user_text},
                ],
                temperature=0.2,
            )

            traduccion = chat_completion.choices[0].message.content.strip()

            payload = {
                "type": "broadcast_message",
                "message": {
                    "type": "prediccion",
                    "text": traduccion,
                    "user": self.username,
                },
                "sender_channel": self.channel_name,
            }

            # a todos menos al emisor
            await self.channel_layer.group_send(self.room_group_name, payload)
            # (opcional) eco al emisor para UI de confirmación
            await self.send(text_data=json.dumps(payload))
            return

        # ---- Mensajes genéricos ----
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signal_message",
                "message": data,
                "sender_channel": self.channel_name,
            },
        )

    # ------------- Handlers de grupo -------------
    async def signal_message(self, event):
        # no se lo envía al emisor
        if self.channel_name != event.get("sender_channel"):
            await self.send(text_data=json.dumps(event["message"]))

    async def broadcast_message(self, event):
        # no se lo envía al emisor
        if self.channel_name != event.get("sender_channel"):
            await self.send(text_data=json.dumps(
                {"type": "broadcast_message", "message": event["message"]}
            ))