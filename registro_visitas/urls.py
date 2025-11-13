from . import views
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"visitas", views.VisitaViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.registrar_visita, name='registrar_visita'),
    path('lista/', views.lista_visitas, name='lista_visitas'),
    path('salida/<int:visita_id>/', views.registrar_salida, name='registrar_salida'),
    path('editar/<int:visita_id>/', views.editar_visita, name='editar_visita'),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    
        # Rutas JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]