from django.contrib import admin
from django.utils import timezone
from .models import Visita


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'rut', 'usuario', 'hora_entrada', 'hora_salida', 'estado')
	list_filter = (('hora_entrada', admin.DateFieldListFilter), 'estado')
	search_fields = ('rut', 'nombre')
	date_hierarchy = 'hora_entrada'
	actions = ['marcar_salida']

	def marcar_salida(self, request, queryset):
		"""Acción masiva para marcar la salida ahora en visitas sin hora_salida."""
		ahora = timezone.now()
		updated = 0
		for visita in queryset:
			if not visita.hora_salida:
				visita.hora_salida = ahora
				visita.estado = Visita.ESTADO_COMPLETADA
				visita.save()
				updated += 1

		self.message_user(request, f"Se marcaron {updated} visitas como salida.")

	marcar_salida.short_description = 'Marcar salida ahora en las visitas seleccionadas'
