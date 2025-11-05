from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import secrets

class HomeView(LoginRequiredMixin, View):
    template_name = 'home/home.html'
    login_url = 'Autenticacion:login'

    def get(self, request,room_name=None):
        room_name = secrets.token_urlsafe(8)
        return render(request, self.template_name , {'user': request.user,'room_name': room_name}) 