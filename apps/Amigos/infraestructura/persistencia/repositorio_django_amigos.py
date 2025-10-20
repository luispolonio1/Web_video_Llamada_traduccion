from django.contrib.auth import get_user_model
from apps.Amigos.dominio.amigos_repositorio import AmigosRepositorio
from typing import List, Dict, Any

User = get_user_model()

class RepositorioDjangoAmigos(AmigosRepositorio):
    def buscar_amigo(self, nombre: str) -> List[Dict[str, Any]]:
        return list(
            User.objects
                .filter(username__icontains=nombre)
                .values('id', 'username')[:20]
        )

        
    def agregar_amigo(self, usuario_id: int, amigo_id: int):
        pass

    def obtener_amigos(self, usuario_id):
        pass