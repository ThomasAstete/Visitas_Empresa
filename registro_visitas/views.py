from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Visita
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from .serializers import GroupSerializer, UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

def validar_rut(rut):
    """
    Valida formato y dígito verificador del RUT chileno.
    Retorna: (bool, mensaje)
    """
    # Limpiar espacios
    rut = rut.strip()
    
    # Validar longitud (9-12 caracteres)
    if len(rut) < 9 or len(rut) > 12:
        return False, "El RUT debe tener entre 9 y 12 caracteres (ej: 12345678-9)"
    
    # Debe tener guión
    if '-' not in rut:
        return False, "El RUT debe contener un guión (ej: 12345678-9)"
    
    # Separar número y dígito verificador
    partes = rut.split('-')
    if len(partes) != 2:
        return False, "Formato incorrecto. Debe ser: 12345678-9"
    
    numero_rut = partes[0]
    dv = partes[1].upper()
    
    # Solo números en la parte principal
    if not numero_rut.isdigit():
        return False, "La parte numérica debe contener solo números"
    
    # 7-8 dígitos en el número
    if len(numero_rut) < 7 or len(numero_rut) > 8:
        return False, "La parte numérica debe tener entre 7 y 8 dígitos"
    
    # Dígito verificador válido (0-9 o K)
    if len(dv) != 1 or (not dv.isdigit() and dv != 'K'):
        return False, "El dígito verificador debe ser un número o K"
    
    # Calcular dígito verificador con algoritmo módulo 11
    def calcular_dv(rut_numero):
        """Calcula DV usando algoritmo oficial chileno"""
        suma = 0
        multiplicador = 2
        
        # Multiplicar cada dígito (derecha a izquierda)
        for digito in reversed(rut_numero):
            suma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        # Aplicar módulo 11
        resto = suma % 11
        dv_calculado = 11 - resto
        
        # Casos especiales
        if dv_calculado == 11:
            return '0'
        elif dv_calculado == 10:
            return 'K'
        else:
            return str(dv_calculado)
    
    # Verificar dígito verificador
    dv_esperado = calcular_dv(numero_rut)
    if dv != dv_esperado:
        return False, f"RUT inválido. El dígito verificador correcto es: {dv_esperado}"
    
    return True, "RUT válido"

def registrar_visita(request):
    """
    Vista para registrar nuevas visitas.
    GET: muestra formulario, POST: procesa datos
    """
    # Fecha actual para mostrar en los templates
    current_date = timezone.localdate()

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        rut = request.POST.get('rut')
        motivo = request.POST.get('motivo')

        # Validar campos obligatorios
        if nombre and rut and motivo:
            # Validar RUT
            rut_valido, mensaje_error = validar_rut(rut)
            
            if rut_valido:
                # Crear registro en BD
                if request.user.is_authenticated:
                    Visita.objects.create(
                        nombre=nombre,
                        rut=rut,
                        motivo=motivo,
                        usuario=request.user,
                    )
                else:
                    Visita.objects.create(
                        nombre=nombre,
                        rut=rut,
                        motivo=motivo,
                    )
                # Redirigir al listado
                return redirect('lista_visitas')
            else:
                # Mostrar error de RUT y preservar datos
                return render(request, 'registro_visitas/formulario_visita.html', {
                    'error': mensaje_error,
                    'nombre_previo': nombre,
                    'rut_previo': rut,
                    'motivo_previo': motivo,
                    'current_date': current_date,
                })
        else:
            # Error por campos faltantes
            return render(request, 'registro_visitas/formulario_visita.html', {
                'error': 'Todos los campos son obligatorios.',
                'nombre_previo': nombre,
                'rut_previo': rut,
                'motivo_previo': motivo,
                'current_date': current_date,
            })

    # Mostrar formulario vacío (GET)
    return render(request, 'registro_visitas/formulario_visita.html', {
        'current_date': current_date
    })

def lista_visitas(request):
    """
    Dashboard de visitas del día actual.
    Muestra estadísticas y listado filtrado por fecha.
    """
    # Obtener fecha local (corregido para timezone Chile)
    hoy = timezone.localdate()
    
    # Filtrar visitas del día
    visitas = Visita.objects.filter(hora_entrada__date=hoy)
    
    # Calcular estadísticas
    visitas_activas = visitas.filter(hora_salida__isnull=True).count()
    visitas_completadas = visitas.filter(hora_salida__isnull=False).count()
    
    return render(request, 'registro_visitas/lista_visitas.html', {
        'visitas': visitas,
        'visitas_activas': visitas_activas,
        'visitas_completadas': visitas_completadas
        , 'current_date': hoy
    })

def registrar_salida(request, visita_id):
    """
    Registra la hora de salida de una visita específica.
    Proceso de check-out de visitantes.
    """
    # Buscar visita por ID
    visita = Visita.objects.get(id=visita_id)
    
    # Marcar hora de salida
    visita.hora_salida = timezone.now()
    visita.save()
    
    # Redirigir al listado
    return redirect('lista_visitas')


def editar_visita(request, visita_id):
    """
    Editar una visita existente (nombre, rut, motivo).
    """
    visita = get_object_or_404(Visita, id=visita_id)
    current_date = timezone.localdate()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        rut = request.POST.get('rut')
        motivo = request.POST.get('motivo')

        if nombre and rut and motivo:
            rut_valido, mensaje_error = validar_rut(rut)
            if not rut_valido:
                return render(request, 'registro_visitas/formulario_visita.html', {
                    'error': mensaje_error,
                    'nombre_previo': nombre,
                    'rut_previo': rut,
                    'motivo_previo': motivo,
                    'edit': True,
                    'visita_id': visita.id,
                    'current_date': current_date,
                })

            # Validación de consistencia de horarios: no permitir que hora_salida < hora_entrada
            if visita.hora_salida and visita.hora_salida < visita.hora_entrada:
                visita.hora_salida = visita.hora_entrada

            visita.nombre = nombre
            visita.rut = rut
            visita.motivo = motivo

            # Asignar usuario si está autenticado
            try:
                if request.user.is_authenticated and not visita.usuario:
                    visita.usuario = request.user
            except Exception:
                pass

            visita.save()
            return redirect('lista_visitas')
        else:
            return render(request, 'registro_visitas/formulario_visita.html', {
                'error': 'Todos los campos son obligatorios.',
                'nombre_previo': nombre,
                'rut_previo': rut,
                'motivo_previo': motivo,
                'edit': True,
                'visita_id': visita.id,
                'current_date': current_date,
            })

    # GET: rellenar formulario con datos existentes
    return render(request, 'registro_visitas/formulario_visita.html', {
        'nombre_previo': visita.nombre,
        'rut_previo': visita.rut,
        'motivo_previo': visita.motivo,
        'edit': True,
        'visita_id': visita.id,
        'current_date': current_date,
    })