import secrets
from django.shortcuts import render
from django.views import View
from apps.usuario.dominio.models import Usuario
from django.http import JsonResponse


class Amigos_get(View):
    def get(self, request):
        amigos = Usuario.objects.filter(amigo=request.user)
        room_name = secrets.token_urlsafe(8)
        amigos_list = [
            {
                'username': amigo.username,
                'id': amigo.id,
                'room_name': room_name
            }
            for amigo in amigos
        ]
        return JsonResponse({'amigos': amigos_list})