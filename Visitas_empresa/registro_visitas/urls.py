from django.urls import path
from . import views

"""
Configuración de URLs para la aplicación registro_visitas.

Este archivo define el mapeo entre URLs y las vistas correspondientes.
Implementa el patrón URL -> Vista -> Template de Django.

URLs disponibles:
- / : Página principal con formulario de registro
- /lista/ : Dashboard con listado de visitas del día
- /salida/<id>/ : Endpoint para registrar salida de una visita específica
"""

urlpatterns = [
    path('', views.registrar_visita, name='registrar_visita'),
    path('lista/', views.lista_visitas, name='lista_visitas'),
    path('salida/<int:visita_id>/', views.registrar_salida, name='registrar_salida'),
]