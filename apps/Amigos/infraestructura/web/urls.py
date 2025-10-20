from django.urls import path
from apps.Amigos.infraestructura.web.buscar_amigos import BuscarAmigosView

app_name = "Amigos"

urlpatterns = [
    path("buscar_amigos/", BuscarAmigosView.as_view(), name="buscar_amigos"),
]