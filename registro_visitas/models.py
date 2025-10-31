from django.db import models
from django.conf import settings
from django.utils import timezone

class Visita(models.Model):
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre completo",
        help_text="Nombre y apellido del visitante"
    )
    
    rut = models.CharField(
        max_length=12,
        verbose_name="RUT",
        help_text="RUT chileno en formato 12345678-9"
    )
    
    motivo = models.TextField(
        verbose_name="Motivo de la visita", 
        help_text="Descripción del propósito de la visita"
    )
    
    hora_entrada = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Hora de entrada",
        help_text="Timestamp automático al registrar la visita"
    )

    hora_salida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Hora de salida",
        help_text="Timestamp de salida del visitante (opcional)"
    )

    # Usuario que registra la visita (relación con el modelo de usuario)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='visitas_registradas',
        verbose_name='Usuario que registra'
    )

    # Estado redundante para facilitar consultas y visualización
    ESTADO_EN_CURSO = 'en_curso'
    ESTADO_COMPLETADA = 'completada'
    ESTADO_CHOICES = [
        (ESTADO_EN_CURSO, 'En curso'),
        (ESTADO_COMPLETADA, 'Completada'),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_EN_CURSO,
        verbose_name='Estado'
    )

    def __str__(self):
        return f"{self.nombre} ({self.rut}) - {self.hora_entrada.date()} [{self.get_estado_display()}]"
    
    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        
        ordering = ['-hora_entrada']
        
        indexes = [
            models.Index(fields=['hora_entrada']), 
            models.Index(fields=['rut']),           
        ]

    def save(self, *args, **kwargs):
        """
        Asegura consistencia del estado en función de la hora_salida.
        """
        if self.hora_salida:
            self.estado = self.ESTADO_COMPLETADA
        else:
            self.estado = self.ESTADO_EN_CURSO

        # Si hora_salida fue seteada y es anterior a hora_entrada, corregir a hora_entrada
        try:
            if self.hora_salida and self.hora_entrada and self.hora_salida < self.hora_entrada:
                # En caso raro, forzamos hora_salida a hora_entrada
                self.hora_salida = self.hora_entrada
        except Exception:
            # Si hora_entrada no está definida todavía (por ejemplo pre-save), ignorar
            pass

        super().save(*args, **kwargs)