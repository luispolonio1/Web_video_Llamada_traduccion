from apps.Autenticacion.dominio.Autenticacion_repositorio import AutenticacionRepositorio
from apps.usuario.dominio.models import Usuario

class AutenticacionCasoUso:
    def __init__(self, repositorio: AutenticacionRepositorio):
        self.repositorio = repositorio

    def iniciar_sesion(self,username: str, password: str) -> Usuario:
        usuario = self.repositorio.iniciar_sesion(username, password)
        if usuario is None:
            raise ValueError("Credenciales inválidas")
        return usuario

    def cambiar_contrasena(self, username: str, old: str, new: str) -> None:
        self.repositorio.cambiar_contrasena(username, old, new)
