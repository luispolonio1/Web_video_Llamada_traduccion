from django.urls import path
from .home_views import HomeView
from .amigos_get import Amigos_get
from .solicitudes_amigos_get import Solicitudes_amigos_get

app_name = "home"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('<str:room_name>/',HomeView.as_view(), name='home_room'),
    path("get/solicitudes_amigos_get/", Solicitudes_amigos_get.as_view(), name="solicitudes_amigos_get"),
    path("<str:room_name>/get/solicitudes_amigos_get/", Solicitudes_amigos_get.as_view(), name="solicitudes_amigos_get_room"),
    path("get/amigos_get/", Amigos_get.as_view(), name="amigos_get"),
    path("<str:room_name>/get/amigos_get/", Amigos_get.as_view(), name="amigos_get_room"),
]