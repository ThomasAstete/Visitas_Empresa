"""
Configuración principal de URLs del proyecto Visitas_empresa.

Este archivo es el punto de entrada principal para el enrutamiento
de URLs en todo el proyecto Django. Define las rutas de nivel superior
y delega a las aplicaciones específicas.

Estructura de URLs:
- /admin/ : Panel de administración de Django
- / : Todas las URLs de la aplicación registro_visitas
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registro_visitas.urls')),
]