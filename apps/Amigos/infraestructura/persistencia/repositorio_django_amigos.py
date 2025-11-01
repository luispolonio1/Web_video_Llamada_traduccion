from django.contrib.auth import get_user_model
from apps.Amigos.dominio.amigos_repositorio import AmigosRepositorio
from typing import List, Dict, Any
from apps.Amigos.models import FriendRequest
from django.shortcuts import get_object_or_404

User = get_user_model()

class RepositorioDjangoAmigos(AmigosRepositorio):
    def buscar_amigo(self, nombre: str) -> List[Dict[str, Any]]:
        return list(
            User.objects
                .filter(username__icontains=nombre)
                .values('id', 'username')[:20]
        )

        
    def agregar_amigo(self, usuario_id: int):
        return User.objects.filter(id=usuario_id).first()
    
    def aceptar_amigo(self, solicitud_id: int, to_user: int):
        return get_object_or_404(FriendRequest, id=solicitud_id, to_user=to_user)

    def rechazar_amigo(self, Solicitud_id: int):
        pass

    def obtener_amigos(self, usuario_id):
        pass