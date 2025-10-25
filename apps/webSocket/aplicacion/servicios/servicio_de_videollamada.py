from ...dominio.puertos.mensajes_puerto import Socket
from ...dominio.entidades.entidades_socket import CallEvent


class VideoCallService:
    def __init__(self, socket_port: Socket):
        self.socket = socket_port

    async def notificar_union(self, username: str):
        evento = CallEvent(
            event_type="joined",
            username=username,
            message=f"🔔 {username} se ha unido a la llamada",
            joined=True
        )
        await self.socket.send_message(evento.__dict__)

    async def notificar_salida(self, username: str):
        evento = CallEvent(
            event_type="left",
            username=username,
            message=f"{username} ha salido de la llamada",
            left=True
        )
        await self.socket.send_message(evento.__dict__)

    async def manejar_mensaje(self, data: dict):
        await self.socket.receive_message(data)
