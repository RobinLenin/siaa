from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from app.core.utils.enums import MensajesEnum
from app.organico.forms import UAAForm
from app.organico.models import UAA

@login_required
@permission_required('organico.view_uaa', raise_exception=True, )
def uaa_estructura(request):
    """
    Muestra toda la estructura del organico estructural
    :param request:
    :return:
    """
    navegacion = ('Módulo de Orgánico Estructural',
                  [('Orgánico estructural', reverse('organico:uaa_estructura'))])
    uaas = UAA.objects.filter(uaa=None)
    return render(request, 'organico/uaa_estructura.html', locals())


@login_required
@permission_required('organico.add_uaa', raise_exception=True, )
def uaa_crear(request, padre_id):
    """
    Muestra la interfaz para crear una nueva UAA, siempre se creara bajo un padre
    :param request:
    :param padre_id:
    :return:
    """
    uaa_padre = get_object_or_404(UAA, id=padre_id)
    uaa_form = UAAForm(initial={'uaa': uaa_padre.id})

    navegacion = ('Módulo de Orgánico Estructural',
                  [('Orgánico estructural', reverse('organico:uaa_estructura')),
                   (uaa_padre, reverse('organico:uaa_detalle', args=[uaa_padre.id])),
                   ('Nuevo UAA', None)])

    return render(request, 'organico/uaa_editar.html', locals())


@login_required
@permission_required('organico.view_uaa', raise_exception=True, )
def uaa_detalle(request, id):
    """
    Se visualiza una UAA
    :param request:
    :param id:
    :return:
    """
    uaa = get_object_or_404(UAA, id=id)
    navegacion = ('Módulo de Orgánico Estructural',
                  [('Orgánico estructural', reverse('organico:uaa_estructura')),
                   (uaa, None)])
    return render(request, 'organico/uaa_detalle.html', locals())


@login_required
@permission_required('organico.change_uaa', raise_exception=True, )
def uaa_editar(request, id):
    """
    Muestra la infertaz para editar una UAA, puede tener un padre o no
    :param request:
    :param id:
    :return:
    """
    uaa = UAA.objects.get(id=id)
    uaa_padre = uaa.uaa
    uaa_form = UAAForm(instance=uaa)

    navegacion = ('Módulo de Orgánico Estructural',
                  [('Orgánico estructural', reverse('organico:uaa_estructura')),
                   (uaa, reverse('organico:uaa_detalle', args=[id])),
                   ('Editar UAA', None)])

    return render(request, 'organico/uaa_editar.html', locals())


@login_required
@permission_required('organico.delete_uaa', raise_exception=True, )
def uaa_eliminar(request, id):
    """
    Elimina un registro UAA
    :param request:
    :param id:
    :return:
    """
    uaa = get_object_or_404(UAA, id=id)
    uaa_id = uaa.uaa.id
    uaa.delete()
    return HttpResponseRedirect(reverse('organico:uaa_detalle', args=(uaa_id,)))


@login_required
@permission_required('organico.add_uaa', 'organico.change_uaa', raise_exception=True, )
def uaa_guardar(request):
    """
    Crea o actualiza un registro de uaa
    :param request:
    :return:
    """
    id = request.POST.get('id')
    uaa_padre_id = request.POST.get('uaa')
    uaa_padre = None if uaa_padre_id is None or uaa_padre_id=='' else UAA.objects.get(id=uaa_padre_id)

    try:
        # Puede editar una uaa con o sin padre
        uaa = get_object_or_404(UAA, id=id)
        estructura = [('Orgánico estructural', reverse('organico:uaa_estructura')),
                      (uaa, reverse('organico:uaa_detalle', args=[uaa.id])),
                      ('Editar UAA', None)]
    except:
        # Siempre tendra una uaa padre si el nuevo
        uaa = UAA()
        estructura = [('Orgánico estructural', reverse('organico:uaa_estructura')),
                      (uaa_padre, reverse('organico:uaa_detalle', args=[uaa_padre.id])),
                      ('Nuevo UAA', None)]

    uaa_form = UAAForm(request.POST, instance=uaa)
    if uaa_form.is_valid():
        uaa = uaa_form.save(commit=False)
        if uaa_padre:
            uaa.uaa = uaa_padre
            uaa.estructura_organizacional = uaa_padre.estructura_organizacional
        uaa.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(reverse('organico:uaa_detalle', args=(uaa.id,)))
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        navegacion = ('Módulo de Orgánico Estructural', estructura)

    return render(request, 'organico/uaa_editar.html', locals())


