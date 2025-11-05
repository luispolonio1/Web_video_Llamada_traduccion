from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.Amigos.models import FriendRequest
from django.http import JsonResponse

class Solicitudes_amigos_get(LoginRequiredMixin, View):
    def get(self, request,room_name=None):
        Solicitudes = FriendRequest.objects.filter(to_user=request.user, status='pending')
        solicitudes_list = [
            {
                'from_user_username': solicitud.from_user.username,
                'solicitud_id': solicitud.id,
            }
            for solicitud in Solicitudes
        ]
        return JsonResponse({'solicitudes': solicitudes_list})