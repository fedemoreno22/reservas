from django.contrib import admin
from .models import Cancha, Reserva, TurnoDisponible, HorarioDisponible

# Register your models here.


admin.site.register(Cancha)
admin.site.register(Reserva)
admin.site.register(TurnoDisponible)
admin.site.register(HorarioDisponible)

class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('cancha', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter = ('cancha', 'fecha')