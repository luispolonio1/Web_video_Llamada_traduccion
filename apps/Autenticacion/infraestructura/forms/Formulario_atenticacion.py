from django.contrib.auth.forms import UserCreationForm
from apps.usuario.dominio.models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'password1', 'password2')