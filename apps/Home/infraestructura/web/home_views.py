from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(LoginRequiredMixin, View):
    template_name = 'home/home.html'
    login_url = 'Autenticacion:login'


    def get(self, request):
        return render(request, self.template_name , {'user': request.user}) 