from abc import ABC, abstractmethod

class AutenticacionRepositorio(ABC):
    @abstractmethod
    def iniciar_sesion(self, nombre_usuario: str, contrasena: str) -> bool:
        pass

    @abstractmethod
    def cambiar_contrasena(self, nombre_usuario: str, contrasena_vieja: str, contrasena_nueva: str) -> bool:
        pass