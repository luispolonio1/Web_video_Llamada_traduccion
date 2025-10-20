from django.http import JsonResponse
from django.views import View
from apps.Amigos.aplicacion.amigos_caso_uso import AmigosCasoUso
from apps.Amigos.infraestructura.persistencia.repositorio_django_amigos import RepositorioDjangoAmigos

class BuscarAmigosView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.auth_use_case = AmigosCasoUso(repositorio=RepositorioDjangoAmigos())

    def get(self, request):
        try:
            nombre = (request.GET.get('nombre') 
                      or request.GET.get('q') 
                      or '').strip()

            if not nombre:
                return JsonResponse({"error": "Parámetro 'nombre' vacío"}, status=400)

            amigos = self.auth_use_case.buscar_amigo(nombre)
            amigos_data = [{'id': r['id'], 'nombre': r['username']} for r in amigos]
            return JsonResponse({"amigos": amigos_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
