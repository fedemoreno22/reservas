from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import calendar 

# Create your models here.


class Cancha(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='canchas/', blank=True, null=True)  # 👉 campo nuevo

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return f"{self.nombre_cliente} - {self.cancha} - {self.fecha}"

class TurnoDisponible(models.Model):
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    dias = models.CharField(max_length=20)  # Por ejemplo: "Lunes,Martes,Miércoles"

    def __str__(self):
        return f"{self.cancha.nombre} - {self.hora_inicio} a {self.hora_fin}"

class HorarioDisponible(models.Model):
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.cancha} - {self.fecha} {self.hora_inicio} a {self.hora_fin}"
    
class Turno(models.Model):
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    fecha = models.DateField()
    horario_disponible = models.ForeignKey(HorarioDisponible, on_delete=models.CASCADE)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    cancelado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cancha} - {self.fecha} - {self.horario_disponible}"
