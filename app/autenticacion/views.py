from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from app.autenticacion.forms import EditarContrasenaForm
from app.core.utils import ldap as conexion_ldap
from app.seguridad.models import Usuario


def cambiar_contrasena(request):
    """
    Cambia la contraseña del usuario logueado
    :param request:
    :return:
    """
    try:
        perfil = request.user.perfil
    except Exception as e:
        print('')

    form = EditarContrasenaForm
    if request.method == 'POST':
        form = EditarContrasenaForm(request.POST)
        if request.user.check_password('{}'.format(request.POST.get('actual_password'))):
            form.password_verificada()

        if form.is_valid():
            valor = form.cleaned_data['password']
            try:
                validate_password(valor, request.user)
            except ValidationError as e:
                print(e)
                form.add_error('password', e)
                return render(request, 'autenticacion/cambiar_contrasena.html', {'form': form})

            request.user.force_password = False
            request.user.password = make_password(valor)
            if request.user.ldap and settings.LDAP_ACTIVE:
                if conexion_ldap.modificar_password_by_usuario_ldap(request.user, valor):
                    request.user.save()
                    messages.success(request, "Datos actualizados correctamente... Ingrese con sus nuevas credenciales")
                else:
                    messages.error(request, "No se pudo actualizar el servidor de autenticacion")
            else:
                request.user.save()
                messages.success(request, "Datos actualizados correctamente... ")

            return HttpResponseRedirect('/')
        else:
            messages.warning(request, "Por favor ingrese todos los datos... ")
    else:
        form = EditarContrasenaForm()
    return render(request, 'autenticacion/cambiar_contrasena.html', locals())


def cerrar_sesion(request):
    """
    Cerrar sesión del usuario logueado
    :param request:
    :return:
    """
    logout(request)
    return HttpResponseRedirect('/')


def iniciar_sesion(request):
    """
    Verifica las credenciales e inicia sesión el usuario
    :param request:
    :return:
    """
    next = ""
    SAC_URL = settings.SAC_URL
    LDAP_ACTIVE = settings.LDAP_ACTIVE

    if request.GET:
        next = request.GET['next']

    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            nombre_usuario = request.POST['username']
            if str(nombre_usuario).find('@unl.edu.ec') < 0:
                nombre_usuario = nombre_usuario + '@unl.edu.ec'
            usuario = Usuario.objects.filter(correo_electronico_institucional=nombre_usuario).first()
            clave = request.POST['password']
            acceso = None

            if usuario:
                if usuario.activo:
                    if settings.LDAP_ACTIVE and usuario:
                        if conexion_ldap.autenticar_siaaf(nombre_usuario, clave):
                            usuario.ldap = True
                            acceso = authenticate(correo_electronico_institucional=nombre_usuario, password=clave)
                        else:
                            messages.warning(request,
                                             "Las datos proporcionados no coinciden con el servidor de autenticación")
                    else:
                        acceso = authenticate(correo_electronico_institucional=nombre_usuario, password=clave)

                    if acceso:
                        login(request, acceso)
                        if acceso.force_password:
                            return HttpResponseRedirect(reverse('autenticacion:cambiar_contrasena'))
                        elif next == "":
                            return HttpResponseRedirect(reverse('index'))
                        else:
                            return HttpResponseRedirect(next)
                    else:
                        messages.warning(request, "Datos de acceso incorrectos. Usuario o contraseña incorrecta... ")
                else:
                    messages.warning(request, "Datos de acceso incorrectos. Usuario no está activo...")
            else:
                messages.warning(request, "Datos de acceso incorrectos. Usuario no existe... ")
    else:
        formulario = AuthenticationForm()

    return render(request, 'autenticacion/iniciar_sesion.html', locals())
