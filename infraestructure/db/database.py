# src/infrastructure/db/database.py
from django.conf import settings
from typing import Dict, Any

class DatabaseConfig:
    @staticmethod
    def get_database_config() -> Dict[Any, Any]:
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',  # O el motor que uses
                'NAME': settings.DB_NAME,
                'USER': settings.DB_USER,
                'PASSWORD': settings.DB_PASSWORD,
                'HOST': settings.DB_HOST,
                'PORT': settings.DB_PORT,
            }
        }

    @staticmethod
    def get_connection():
        # Método para obtener una conexión directa si es necesario
        pass