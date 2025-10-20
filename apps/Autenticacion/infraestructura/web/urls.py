from django.urls import path
from .Autenticacion import LoginView, RegisterView, LogoutView

app_name = "Autenticacion"

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("registro/", RegisterView.as_view(), name="registro"),
    path("logout/", LogoutView.as_view(), name="logout"),
]