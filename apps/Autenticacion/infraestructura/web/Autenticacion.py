from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

from apps.Autenticacion.aplicacion.Autenticacion_caso_uso import AutenticacionCasoUso
from apps.Autenticacion.infraestructura.persistencia.repositorio_django import RepositorioAutenticacionDjango
from apps.Autenticacion.infraestructura.forms.Formulario_atenticacion import UsuarioCreationForm

class LoginView(View):
    template_name = 'auth/Login.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.auth_use_case = AutenticacionCasoUso(
            repositorio=RepositorioAutenticacionDjango()
        )

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home:home')
        return render(request, self.template_name, {'form': AuthenticationForm()})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'error': 'Credenciales inválidas'})

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        try:
            user = self.auth_use_case.iniciar_sesion(username, password)
            login(request, user)
            return redirect('home:home')
        except ValueError:
            return render(request, self.template_name, {'form': form, 'error': 'Credenciales inválidas'})


class RegisterView(View):
    template_name = 'auth/Registro.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.auth_use_case = AutenticacionCasoUso(
            repositorio=RepositorioAutenticacionDjango()
        )

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home:home')
        return render(request, self.template_name, {'form': UsuarioCreationForm()})

    def post(self, request):
        form = UsuarioCreationForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'error': 'Error en el registro'})

        user = form.save()
        login(request, user)
        return redirect("home:home")


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('Autenticacion:login')