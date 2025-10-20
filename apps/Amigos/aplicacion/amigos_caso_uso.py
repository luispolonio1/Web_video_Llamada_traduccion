from apps.Amigos.dominio.amigos_repositorio import AmigosRepositorio
from apps.usuario.dominio.models import Usuario
from typing import List, Dict, Any


class AmigosCasoUso:
    def __init__(self, repositorio: AmigosRepositorio):
        self.repositorio = repositorio

    def buscar_amigo(self, nombre:str) -> List[Dict[str, Any]]:
        return self.repositorio.buscar_amigo(nombre)
    
    def agregar_amigo(self, usuario_id: int, amigo_id: int) -> None:
        return self.repositorio.agregar_amigo(usuario_id, amigo_id)
    
    def obtener_amigos(self, usuario_id: int) -> list[Usuario]:
        return self.repositorio.obtener_amigos(usuario_id)