from django.http import JsonResponse
from django.views import View
from apps.Amigos.aplicacion.amigos_caso_uso import AmigosCasoUso
from apps.Amigos.infraestructura.persistencia.repositorio_django_amigos import RepositorioDjangoAmigos
from apps.Amigos.models import FriendRequest
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class AgregarAmigosView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.auth_use_case = AmigosCasoUso(repositorio=RepositorioDjangoAmigos())

    def post(self, request,user_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Usuario no autenticado"}, status=401)
        print(user_id)
        to_user = self.auth_use_case.agregar_amigo(user_id)

        fr , created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={'status': 'pending'}
        )

        if not created:
            return JsonResponse({"message": "Solicitud de amistad ya enviada"}, status=400)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{to_user.id}",
            {
                "type": "nueva_solicitud_amistad",
                "Solicitud":{
                    'id': fr.id,
                    'from_user': fr.from_user.username,
                }
            }
        )
        return JsonResponse({"message": "Solicitud de amistad enviada"}, status=200)