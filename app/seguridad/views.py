from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from app.core.models import Expediente
from app.seguridad.models import Usuario


@login_required
def usuario_perfil(request):
    """
    Muestra información detallada relacionada al perfil del usuario que esta autenticado. La mayoria de información
    esta relacionada al expediente, por ello aseguramos que existe el registro expediente
    :param request:
    :return:
    """
    usuario = request.user
    navegacion = ('Perfil de %s' % request.user.persona.get_nombres_completos(),
                  [('Inicio', reverse('index')), ('Perfil de usuario', None)])
    try:
        usuario.persona.expediente
    except:
        expediente = Expediente(persona=usuario.persona)
        expediente.save()

    return render(request, 'seguridad/usuario/informacion_detallada.html', locals())


@login_required
def usuario_actualizar_fotografia(request, id):
    """
    Carga la fotografía desde la cuenta de google asociada, dado el identificador de usuario
    :param request:
    :param id:
    :return:
    """
    try:
        usuario = Usuario.objects.get(id=id)
        next = request.GET.get('next')
        usuario.vincular_google()

        if usuario.foto_url:
            messages.success(request, 'La fotografía se cargo exitosamente')
        else:
            messages.warning(request, 'No pudo cargarse la fotografía')

        return HttpResponseRedirect(next)

    except Exception:

        return HttpResponseRedirect('/')
