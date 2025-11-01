from django.http import JsonResponse
from django.views import View
from apps.Amigos.aplicacion.amigos_caso_uso import AmigosCasoUso
from apps.Amigos.infraestructura.persistencia.repositorio_django_amigos import RepositorioDjangoAmigos
from apps.Amigos.models import FriendRequest
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class AceptarAmigosView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.auth_use_case = AmigosCasoUso(repositorio=RepositorioDjangoAmigos())

    def post(self,request,solicitud_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Usuario no autenticado"}, status=401)
        
        solicitud = self.auth_use_case.aceptar_amigo(solicitud_id,request.user)

        if solicitud.status != "pending":
            return JsonResponse({"error": "La solicitud ya ha sido procesada"}, status=400)
        
        solicitud.status = "accepted"
        solicitud.save()

        request.user.amigo.add(solicitud.from_user)
        solicitud.from_user.amigo.add(request.user)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        f'user_{request.user.id}',
        {
            'type': 'nuevo_amigo',
            'amigo': {
                'id': solicitud.from_user.id,
                'username': solicitud.from_user.username,
            }
        }
        )
        async_to_sync(channel_layer.group_send)(
            f'user_{solicitud.from_user.id}',
            {
                'type': 'nuevo_amigo',
                'amigo': {
                    'id': request.user.id,
                    'username': request.user.username,
                }
            }
        )
    
        return JsonResponse({"message": "Solicitud aceptada"})
