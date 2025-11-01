from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AmigosRepositorio(ABC):
    @abstractmethod
    def buscar_amigo(self, nombe:str) -> List[Dict[str, Any]]:
        """Busca un amigo en la aplicacion web."""
        pass

    @abstractmethod
    def agregar_amigo(self, usuario_id: int) -> None:
        """Agrega un amigo a la lista de amigos del usuario."""
        pass

    @abstractmethod
    def obtener_amigos(self, usuario_id: int) -> list:
        """Obtiene la lista de amigos del usuario."""
        pass