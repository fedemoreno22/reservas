"""
URL configuration for reservas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.contrib import admin
from turnos import views
from django.urls import path
from django.shortcuts import redirect
from turnos.views import CustomLoginView, logout_view, CustomPasswordResetView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ajax/horarios/', views.ajax_cargar_horarios, name='ajax_cargar_horarios'),
    path('', views.portada, name='portada'),
    path('reservar/', views.reservar_turno, name='reservar_turno'),
    path('exito/', views.turno_exito, name='turno_exito'),
    path('registro/', views.registro, name='registro'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas-admin/', views.reservas_admin, name='reservas_admin'),  # ✅ SOLO UNA VEZ
    path('portada/', views.portada, name='portada'),
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('editar_reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('horarios-disponibles/', views.obtener_horarios_disponibles, name='horarios_disponibles'),
    path('ajax/horarios-disponibles/', views.obtener_horarios_disponibles, name='horarios_disponibles'),
    path('api/horarios-disponibles/', views.obtener_horarios_disponibles, name='obtener_horarios'),
    path('obtener-horarios/', views.obtener_horarios_disponibles, name='obtener_horarios'),
    path('horarios/nuevo/', views.crear_horario, name='crear_horario'),
    path('horarios/configurar/', views.configurar_horarios, name='configurar_horarios'),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


