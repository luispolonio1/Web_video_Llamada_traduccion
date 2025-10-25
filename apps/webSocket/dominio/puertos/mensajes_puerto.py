from abc import ABC, abstractmethod
from typing import Any, Dict

class Socket(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """Establece la conexión con el socket."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Cierra la conexión."""
        pass

    @abstractmethod
    async def send_message(self, message: Any) -> None:
        """Envía un mensaje a través del socket."""
        pass

    @abstractmethod
    async def receive_message(self, data: Dict[str, Any]) -> None:
        """Procesa un mensaje recibido."""
        pass
