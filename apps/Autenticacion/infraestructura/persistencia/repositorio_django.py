from django.contrib.auth import authenticate, get_user_model
from apps.Autenticacion.dominio.Autenticacion_repositorio import AutenticacionRepositorio

User = get_user_model()

class RepositorioAutenticacionDjango(AutenticacionRepositorio):
    def iniciar_sesion(self, nombre_usuario: str, contrasena: str):
        return authenticate(username=nombre_usuario, password=contrasena)

    def cambiar_contrasena(self, nombre_usuario: str, contrasena_vieja: str, contrasena_nueva: str) -> bool:
        try:
            user = User.objects.get(username=nombre_usuario)
        except User.DoesNotExist:
            return False
        if not user.check_password(contrasena_vieja):
            return False
        user.set_password(contrasena_nueva)
        user.save()
        return True