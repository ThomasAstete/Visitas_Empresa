from django.db import models

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

    def __str__(self):
        return f"{self.nombre} ({self.rut}) - {self.hora_entrada.date()}"
    
    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        
        ordering = ['-hora_entrada']
        
        indexes = [
            models.Index(fields=['hora_entrada']), 
            models.Index(fields=['rut']),           
        ]