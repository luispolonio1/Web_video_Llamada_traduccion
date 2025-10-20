from django.urls import path
from .home_views import HomeView

app_name = "home"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]