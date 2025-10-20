from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
    amigo = models.ManyToManyField('self',symmetrical=True, blank=True)
