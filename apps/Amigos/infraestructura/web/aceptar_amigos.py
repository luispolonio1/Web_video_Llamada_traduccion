from django.http import JsonResponse
from django.views import View
from apps.Amigos.aplicacion.amigos_caso_uso import AmigosCasoUso
from apps.Amigos.infraestructura.persistencia.repositorio_django_amigos import RepositorioDjangoAmigos


class AceptarAmigosView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.auth_use_case = AmigosCasoUso(repositorio=RepositorioDjangoAmigos())

    def post(self,request,solicitud_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Usuario no autenticado"}, status=401)
        
        solicitud = self.auth_use_case.aceptar_amigo(solicitud_id,request.user)
        print(solicitud)

        if solicitud.status != "pending":
            return JsonResponse({"error": "La solicitud ya ha sido procesada"}, status=400)
        
        solicitud.status = "accepted"
        solicitud.save()

        request.user.amigo.add(solicitud.from_user)
        solicitud.from_user.amigo.add(request.user)
    
        return JsonResponse({"message": "Solicitud aceptada"})
