from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from app.core.forms import RelacionForm, PersonaBuscarForm, DireccionForm, PersonaForm
from app.core.models import *
from app.core.utils.enums import MensajesEnum


@login_required
def direccion_crear(request, persona_id):
    """
    Muestra la interfaz para crear una dirección  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=persona_id)
    direccion_form = DireccionForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_direccion'),
                       ('Dirección', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_direccion'),
                       ('Dirección', None)])

    return render(request, 'core/direccion/editar.html', locals())


@login_required
def direccion_editar(request, id):
    """
    Muestra el registro para editar una dirección y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    direccion = Direccion.objects.get(id=id)
    persona = Persona.objects.get(id=direccion.persona.id)
    direccion_form = DireccionForm(instance=direccion)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_direccion'),
                       ('Dirección', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_direccion'),
                       ('Dirección', None)])

    return render(request, 'core/direccion/editar.html', locals())


@login_required
def direccion_eliminar(request, id):
    """
    Elimina un registro direccion, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    direccion = Direccion.objects.get(id=id)
    direccion.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next + '#tab_direccion')


@login_required
def direccion_guardar(request, persona_id):
    """
    Crea o actualiza un registro de direccion, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        direccion = get_object_or_404(Direccion, id=id)
    except:
        direccion = Direccion()

    persona = Persona.objects.get(id=persona_id)
    direccion_form = DireccionForm(request.POST, instance=direccion)

    if direccion_form.is_valid():
        direccion = direccion_form.save(commit=False)
        direccion.persona = persona
        direccion.parroquia_id = request.POST['parroquia']
        direccion.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

        return HttpResponseRedirect(next + '#tab_direccion')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_direccion'),
                           ('Dirección', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[persona.usuario.funcionario.id]) + '#tab_direccion'),
                           ('Dirección', None)])

    return render(request, 'core/direccion/editar.html', locals())


@login_required
def persona_editar(request, id):
    """
    Muestra el registro para editar una persona y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=id)
    persona_form = PersonaForm(instance=persona)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil')),
                       ('Datos personales', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id])),
                       ('Datos personales', None)])

    return render(request, 'core/persona/editar.html', locals())


@login_required
def persona_guardar(request):
    """
    Crea o actualiza un registro de persona, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        persona = get_object_or_404(Persona, id=id)
    except:
        persona = Persona()

    persona_form = PersonaForm(request.POST, instance=persona)

    if persona_form.is_valid():
        persona_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next)

    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil')),
                           ('Datos personales', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario', args=[persona.usuario.funcionario.id])),
                           ('Datos personales', None)])

    return render(request, 'core/persona/editar.html', locals())


@login_required
def relacion_buscar(request, persona_id):
    """
    En la interfaz de relación familiar busca la persona para autocompletar datos de la
    relación familiar, es invocado desde perfil y modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.POST.get('next')
    persona = Persona.objects.get(id=persona_id)
    persona_buscar_form = PersonaBuscarForm(request.POST)
    if persona_buscar_form.is_valid():
        relacion = Relacion()
        relacion.numero_documento = request.POST['criterio']
        try:
            relacion_persona = Persona.objects.get(numero_documento=request.POST['criterio'])
            relacion.nombres = relacion_persona.get_nombres()
            relacion.apellidos = relacion_persona.get_apellidos()
            relacion.fecha_nacimiento = relacion_persona.fecha_nacimiento
            relacion.tipo_documento = relacion_persona.tipo_documento
            relacion_form = RelacionForm(instance=relacion)

        except Persona.DoesNotExist:
            messages.warning(request, 'La persona no existe, proceda a ingresar los datos manualmente...')
            relacion_form = RelacionForm(instance=relacion)
    else:
        messages.warning(request, MensajesEnum.ACCION_GUARDAR.value)
        relacion_form = RelacionForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_relacion'),
                       ('Relación familiar', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_relacion'),
                       ('Relación familiar', None)])

    return render(request, 'core/relacion/editar.html', locals())


@login_required
def relacion_crear(request, persona_id):
    """
    Muestra la interfaz para crear una relacion familiar y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=persona_id)
    persona_buscar_form = PersonaBuscarForm()
    relacion_form = RelacionForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_relacion'),
                       ('Relación familiar', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_relacion'),
                       ('Relación familiar', None)])

    return render(request, 'core/relacion/editar.html', locals())


@login_required
def relacion_editar(request, id):
    """
    Muestra el registro para editar una relacion y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    relacion = Relacion.objects.get(id=id)
    persona = Persona.objects.get(id=relacion.expediente.persona.id)
    persona_buscar_form = PersonaBuscarForm()
    relacion_form = RelacionForm(instance=relacion)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_relacion'),
                       ('Relación familiar', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_relacion'),
                       ('Relación familiar', None)])

    return render(request, 'core/relacion/editar.html', locals())


@login_required
def relacion_eliminar(request, id):
    """
    Elimina un registro relacion, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    relacion = Relacion.objects.get(id=id)
    relacion.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next + '#tab_relacion')


@login_required
def relacion_guardar(request, persona_id):
    """
    Crea o actualiza un registro de relacion y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param persona_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        relacion = get_object_or_404(Relacion, id=id)
    except:
        relacion = Relacion()

    persona = Persona.objects.get(id=persona_id)
    persona_buscar_form = PersonaBuscarForm()
    relacion_form = RelacionForm(request.POST, instance=relacion)

    if relacion_form.is_valid():
        numero_documento = relacion_form.cleaned_data['numero_documento']
        relacion_existe = Relacion.objects.filter(expediente=persona.expediente,
                                                  numero_documento=numero_documento).exclude(id=relacion.id).first()
        if relacion_existe is None:
            if numero_documento != persona.numero_documento:
                relacion = relacion_form.save(commit=False)
                relacion.expediente = persona.expediente
                relacion.save()
                messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
                return HttpResponseRedirect(next + '#tab_relacion')
            else:
                messages.warning(request, 'No puede añadirse como familiar o contacto a la misma persona')
        else:
            messages.warning(request, 'Ya posee un registro de relación con el número de documento')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_relacion'),
                       ('Relación familiar', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[persona.usuario.funcionario.id]) + '#tab_relacion'),
                       ('Relación familiar', None)])

    return render(request, 'core/relacion/editar.html', locals())
