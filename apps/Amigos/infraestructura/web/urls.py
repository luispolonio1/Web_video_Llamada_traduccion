from django.urls import path
from apps.Amigos.infraestructura.web.buscar_amigos import BuscarAmigosView
from apps.Amigos.infraestructura.web.agregar_amigos import AgregarAmigosView
from apps.Amigos.infraestructura.web.aceptar_amigos import AceptarAmigosView

app_name = "Amigos"

urlpatterns = [
    path("buscar_amigos/", BuscarAmigosView.as_view(), name="buscar_amigos"),
    path("agregar_amigos/<int:user_id>/", AgregarAmigosView.as_view(), name="agregar_amigos"),
    path("aceptar_amigos/<int:solicitud_id>/", AceptarAmigosView.as_view(), name="aceptar_amigos"),
]