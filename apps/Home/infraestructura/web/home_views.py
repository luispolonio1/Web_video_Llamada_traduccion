from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.Amigos.models import FriendRequest
from apps.usuario.dominio.models import Usuario
import secrets

class HomeView(LoginRequiredMixin, View):
    template_name = 'home/home.html'
    login_url = 'Autenticacion:login'


    def get(self, request,room_name=None):
        Solicitudes = FriendRequest.objects.filter(to_user=request.user, status='pending')
        amigos = Usuario.objects.filter(amigo=request.user)
        room_name = secrets.token_urlsafe(8)
        print(Solicitudes)
        return render(request, self.template_name , {'user': request.user, 'Solicitudes': Solicitudes, 'amigos': amigos, 'room_name': room_name}) 