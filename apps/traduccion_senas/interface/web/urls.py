from django.urls import path
from . import views

app_name = 'traduccion_senas'

urlpatterns = [
    path('upload-audio/', views.upload_audio, name='upload_audio'),
    path('live-enqueue/', views.live_enqueue, name='live_enqueue'),
]
