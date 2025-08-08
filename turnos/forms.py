from django import forms
from .models import Reserva, Cancha, HorarioDisponible, Turno
from datetime import datetime
from calendar import calendar
from django.db.models import Q
from django import forms


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cancha', 'fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'cancha': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded shadow-sm'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded shadow-sm'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border rounded shadow-sm'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border rounded shadow-sm'}),
        }

class ReservaTurnoForm(forms.Form):
    cancha = forms.ModelChoiceField(queryset=Cancha.objects.all())
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    horario = forms.ChoiceField(choices=[], required=True, label="Horario")
    nombre_cliente = forms.CharField(required=False)

    def cargar_horarios_disponibles(self, cancha_id, fecha):
        horarios_disponibles = HorarioDisponible.objects.filter(cancha_id=cancha_id, fecha=fecha)

        reservas = Reserva.objects.filter(cancha_id=cancha_id, fecha=fecha)
        horarios_filtrados = []

        for h in horarios_disponibles:
            solapada = reservas.filter(
                hora_inicio__lt=h.hora_fin,
                hora_fin__gt=h.hora_inicio
            ).exists()

            if not solapada:
                horario_str = f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')}"
                horarios_filtrados.append((horario_str, horario_str))

        self.fields['horario'].choices = horarios_filtrados



class HorarioDisponibleForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponible
        fields = ['cancha', 'fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cancha', 'fecha', 'horario_disponible']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cancha = self.data.get('cancha')
        fecha = self.data.get('fecha')

        if cancha and fecha:
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                dia_semana = fecha_obj.weekday()  # lunes=0 ... domingo=6

                self.fields['horario_disponible'].queryset = HorarioDisponible.objects.filter(
                    cancha_id=cancha,
                    dia_semana=dia_semana
                ).exclude(
                    Q(turno__fecha=fecha_obj) &
                    Q(turno__cancelado=False)
                ).distinct()
            except ValueError:
                self.fields['horario_disponible'].queryset = HorarioDisponible.objects.none()
        else:
            self.fields['horario_disponible'].queryset = HorarioDisponible.objects.none()

class EditarReservaForm(forms.Form):
    cancha = forms.ModelChoiceField(queryset=Cancha.objects.all())
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    horario = forms.ChoiceField(choices=[], required=False)
    nombre_cliente = forms.CharField(required=False)

    def cargar_horarios_disponibles(self, cancha_id, fecha, reserva_id=None):
        horarios_disponibles = HorarioDisponible.objects.filter(cancha_id=cancha_id, fecha=fecha)
        reservas = Reserva.objects.filter(cancha_id=cancha_id, fecha=fecha).exclude(id=reserva_id)

        horarios_filtrados = []
        for h in horarios_disponibles:
            solapada = reservas.filter(
                hora_inicio__lt=h.hora_fin,
                hora_fin__gt=h.hora_inicio
            ).exists()
            if not solapada:
                horario_str = f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')}"
                horarios_filtrados.append((horario_str, horario_str))

        self.fields['horario'].choices = horarios_filtrados
