
from django.shortcuts import render, redirect, get_object_or_404
from .forms import HorarioDisponibleForm, HorarioDisponible, EditarReservaForm
from .models import Reserva, Cancha, HorarioDisponible, Turno
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView
from .forms import ReservaTurnoForm
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, time, timedelta

@login_required
def reservas_admin(request):
    print("Entró a la vista reservas_admin")  # 👈 TEMPORAL
    if not request.user.is_staff:
        return redirect('mis_reservas')  # o mostrar error si querés

    reservas = Reserva.objects.all().order_by('-fecha', '-hora_inicio')

    # Filtros
    fecha = request.GET.get('fecha')
    cancha_id = request.GET.get('cancha')
    usuario_id = request.GET.get('usuario')

    if fecha:
        reservas = reservas.filter(fecha=fecha)
    if cancha_id:
        reservas = reservas.filter(cancha__id=cancha_id)
    if usuario_id:
        reservas = reservas.filter(usuario__id=usuario_id)

    canchas = Cancha.objects.all()
    usuarios = User.objects.all()

    return render(request, 'turnos/reservas_admin.html', {
        'reservas': reservas,
        'fecha': fecha,
        'cancha_id': cancha_id,
        'usuario_id': usuario_id,
        'canchas': canchas,
        'usuarios': usuarios,
    })

@login_required
def reservar_turno(request):
    cancha_id = request.GET.get('cancha')
    fecha_str = request.GET.get('fecha')

    if request.method == 'POST':
        form = ReservaTurnoForm(request.POST)

        cancha_id = request.POST.get('cancha')
        fecha_str = request.POST.get('fecha')

        if cancha_id and fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                form.cargar_horarios_disponibles(cancha_id, fecha)
            except ValueError:
                pass

        # Si vienen datos pre-cargados (cancha y fecha) los usamos para cargar horarios
        if form.is_valid():
            cancha = form.cleaned_data['cancha']
            fecha = form.cleaned_data['fecha']
            horario = form.cleaned_data['horario']
            hora_inicio_str, hora_fin_str = horario.split('-')
            hora_inicio = datetime.strptime(hora_inicio_str.strip(), '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str.strip(), '%H:%M').time()

            # Verificar solapamiento
            solapadas = Reserva.objects.filter(
                fecha=fecha,
                cancha=cancha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            )
            if solapadas.exists():
                messages.error(request, "Ese horario ya fue reservado.")
            else:
                reserva = Reserva(
                    cancha=cancha,
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )
                if request.user.is_staff:
                    reserva.usuario = None
                    reserva.nombre_cliente = form.cleaned_data.get('nombre_cliente')
                else:
                    reserva.usuario = request.user

                reserva.save()
                messages.success(request, "Tu turno fue reservado correctamente.")
                return redirect('mis_reservas' if not request.user.is_staff else 'reservas_admin')
        else:
            # En caso de error de validación, intentar precargar horarios de nuevo
            cancha = form.cleaned_data.get('cancha')
            fecha = form.cleaned_data.get('fecha')
            if cancha and fecha:
                form.cargar_horarios_disponibles(cancha.id, fecha)
    else:
        initial_data = {}
        if cancha_id:
            initial_data['cancha'] = cancha_id
        if fecha_str:
            initial_data['fecha'] = fecha_str
        form = ReservaTurnoForm(initial=initial_data)

        # Cargar horarios disponibles si ya hay cancha y fecha
        if cancha_id and fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                form.cargar_horarios_disponibles(cancha_id, fecha)
            except ValueError:
                pass  # Fecha inválida, ignoramos

    return render(request, 'turnos/reservar_turno.html', {'form': form})

def turno_exito(request):
    return render(request, 'turnos/exito.html')

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('reservar_turno')
    else:
        form = UserCreationForm()
    return render(request, 'turnos/registro.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'turnos/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Solo este mensaje personalizado
        messages.success(self.request, f"¡Bienvenido, {self.request.user.username}! Ya podés reservar tu cancha 🎉")
        return response

def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('portada')

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha', '-hora_inicio')

    # Filtros
    fecha_busqueda = request.GET.get('fecha')
    cancha_id = request.GET.get('cancha')

    if fecha_busqueda:
        reservas = reservas.filter(fecha=fecha_busqueda)

    if cancha_id:
        reservas = reservas.filter(cancha__id=cancha_id)

    canchas = Cancha.objects.all()

    return render(request, 'turnos/mis_reservas.html', {
        'reservas': reservas,
        'fecha_busqueda': fecha_busqueda,
        'cancha_id': cancha_id,
        'canchas': canchas
    })

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if not (request.user == reserva.usuario or request.user.is_staff):
        messages.error(request, "No tenés permiso para cancelar esta reserva.")
        return redirect('mis_reservas')

    reserva.delete()
    messages.success(request, "La reserva fue cancelada.")
    return redirect('reservas_admin' if request.user.is_staff else 'mis_reservas')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('reservas_admin')  # 👈 redirige a vista admin
            else:
                return redirect('mis_reservas')
        else:
            messages.error(request, 'Credenciales incorrectas')
    return render(request, 'registration/login.html')

def portada(request):
    canchas = Cancha.objects.all()
    hoy = datetime.today().date()

    info_canchas = []
    for cancha in canchas:
        horarios_disponibles = HorarioDisponible.objects.filter(cancha=cancha, fecha__gte=hoy).order_by('fecha', 'hora_inicio')
        proximo = None

        for horario in horarios_disponibles:
            solapada = Reserva.objects.filter(
                cancha=cancha,
                fecha=horario.fecha,
                hora_inicio__lt=horario.hora_fin,
                hora_fin__gt=horario.hora_inicio
            ).exists()
            if not solapada:
                proximo = horario
                break

        info_canchas.append({
            'cancha': cancha,
            'proximo': proximo,
        })

    return render(request, 'turnos/portada.html', {'info_canchas': info_canchas})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Si existe una cuenta con ese correo, recibirás un email para restablecer la contraseña.")
        return super().form_valid(form)

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if not request.user.is_staff and reserva.usuario != request.user:
        return redirect('mis_reservas')

    if request.method == 'POST':
        form = EditarReservaForm(request.POST)
        form.cargar_horarios_disponibles(
        request.POST.get('cancha'),
        request.POST.get('fecha'),
        reserva.id
        )
        if form.is_valid():
            cancha = form.cleaned_data['cancha']
            fecha = form.cleaned_data['fecha']
            horario = form.cleaned_data['horario']
            nombre_cliente = form.cleaned_data.get('nombre_cliente')

            hora_inicio_str, hora_fin_str = horario.split('-')
            hora_inicio = datetime.strptime(hora_inicio_str.strip(), '%H:%M').time()
            hora_fin = datetime.strptime(hora_fin_str.strip(), '%H:%M').time()

            solapadas = Reserva.objects.filter(
                fecha=fecha,
                cancha=cancha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            ).exclude(id=reserva.id)

            if solapadas.exists():
                messages.error(request, "Ese horario ya está reservado.")
            else:
                reserva.cancha = cancha
                reserva.fecha = fecha
                reserva.hora_inicio = hora_inicio
                reserva.hora_fin = hora_fin
                if request.user.is_staff:
                    reserva.usuario = None
                    reserva.nombre_cliente = nombre_cliente
                reserva.save()
                messages.success(request, "Reserva actualizada correctamente.")
                return redirect('reservas_admin' if request.user.is_staff else 'mis_reservas')
    else:
        form = EditarReservaForm(initial={
            'cancha': reserva.cancha,
            'fecha': reserva.fecha.strftime('%Y-%m-%d'),
            'nombre_cliente': reserva.nombre_cliente,
        })
        form.cargar_horarios_disponibles(reserva.cancha.id, reserva.fecha, reserva.id)
        if reserva.hora_inicio and reserva.hora_fin:
            horario_str = f"{reserva.hora_inicio.strftime('%H:%M')} - {reserva.hora_fin.strftime('%H:%M')}"
            form.fields['horario'].choices.insert(0, (horario_str, horario_str))
            form.fields['horario'].initial = horario_str

    return render(request, 'turnos/editar_reserva.html', {'form': form, 'reserva': reserva})

def obtener_horarios_disponibles(request):  # ← ESTE es el nombre correcto
    cancha_id = request.GET.get('cancha_id')
    fecha_str = request.GET.get('fecha')
    if cancha_id and fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            horarios = HorarioDisponible.objects.filter(cancha_id=cancha_id, fecha=fecha)
            data = [
                {
                    'valor': f"{h.hora_inicio}-{h.hora_fin}",
                    'texto': f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')}"
                }
                for h in horarios
            ]
            return JsonResponse({'horarios': data})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Datos incompletos'})

@staff_member_required
def configurar_horarios(request):
    form = HorarioDisponibleForm()
    horarios = HorarioDisponible.objects.all().order_by('-fecha', 'hora_inicio')
    if request.method == 'POST':
        form = HorarioDisponibleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horario agregado correctamente.")
            return redirect('configurar_horarios')
    return render(request, 'turnos/configurar_horarios.html', {'form': form, 'horarios': horarios})

@staff_member_required
def crear_horario(request):
    if request.method == 'POST':
        form = HorarioDisponibleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Horario guardado correctamente.")
            return redirect('configurar_horarios')
    else:
        form = HorarioDisponibleForm()
    return render(request, 'turnos/crear_horario.html', {'form': form})

def ajax_cargar_horarios(request):
    cancha_id = request.GET.get('cancha_id')
    fecha_str = request.GET.get('fecha')

    if not (cancha_id and fecha_str):
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        cancha = Cancha.objects.get(pk=cancha_id)
    except (ValueError, Cancha.DoesNotExist):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    # Obtener horarios disponibles configurados por el administrador
    horarios_disponibles = HorarioDisponible.objects.filter(cancha=cancha, fecha=fecha)

    horarios = []
    for h in horarios_disponibles:
        # Verificamos que no esté reservado ese horario
        ocupado = Reserva.objects.filter(
            cancha=cancha,
            fecha=fecha,
            hora_inicio__lt=h.hora_fin,
            hora_fin__gt=h.hora_inicio
        ).exists()

        if not ocupado:
            texto = f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')}"
            horarios.append({'valor': texto, 'texto': texto})

    return JsonResponse({'horarios': horarios})
