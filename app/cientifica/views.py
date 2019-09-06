from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from app.cientifica.forms import ArticuloRevistaForm, PonenciaForm, CapituloLibroForm, LibroForm
from app.cientifica.models import ProduccionCientifica, ArticuloRevista, Ponencia, CapituloLibro, Libro
from app.core.models import Expediente, Persona
from app.core.utils.enums import MensajesEnum


@login_required
def articulo_revista_crear(request, produccion_cientifica_id):
    """
    Muestra la interfaz para crear un articulo de revista y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.GET.get('next')
    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    articulo_revista_form = ArticuloRevistaForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Artículo de revista', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Artículo de revista', None)])

    return render(request, 'cientifica/articulo_revista/editar.html', locals())


@login_required
def articulo_revista_editar(request, id):
    """
    Muestra la interfaz para editar un articulo de revista y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    articulo_revista = ArticuloRevista.objects.get(id=id)
    produccion_cientifica = articulo_revista.produccion_cientifica
    articulo_revista_form = ArticuloRevistaForm(instance=articulo_revista)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Artículo de revista', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Artículo de revista', None)])

    return render(request, 'cientifica/articulo_revista/editar.html', locals())


@login_required
def articulo_revista_eliminar(request, id):
    """
    Elimina un registro articulo de revista, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    articulo_revista = ArticuloRevista.objects.get(id=id)
    articulo_revista.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
    return HttpResponseRedirect(next + '#tab_produccion_cientifica')


@login_required
def articulo_revista_guardar(request, produccion_cientifica_id):
    """
    Crea o actualiza un articulo de revista y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        articulo_revista = get_object_or_404(ArticuloRevista, id=id)
    except:
        articulo_revista = ArticuloRevista()

    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    articulo_revista_form = ArticuloRevistaForm(request.POST, instance=articulo_revista)

    if articulo_revista_form.is_valid():
        articulo_revista = articulo_revista_form.save(commit=False)
        articulo_revista.produccion_cientifica = produccion_cientifica
        articulo_revista.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_produccion_cientifica')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                           ('Artículo de revista', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (produccion_cientifica.expediente.persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[
                                        produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                           ('Artículo de revista', None)])

    return render(request, 'cientifica/articulo_revista/editar.html', locals())


@login_required
def capitulo_libro_crear(request, produccion_cientifica_id):
    """
    Muestra la interfaz para crear un capitulo de libro  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.GET.get('next')
    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    capitulo_libro_form = CapituloLibroForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Capítulo de Libro', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Capítulo de Libro', None)])

    return render(request, 'cientifica/capitulo_libro/editar.html', locals())


@login_required
def capitulo_libro_editar(request, id):
    """
    Muestra la interfaz para editar un caputilo de libro  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    capitulo_libro = CapituloLibro.objects.get(id=id)
    produccion_cientifica = capitulo_libro.produccion_cientifica
    capitulo_libro_form = CapituloLibroForm(instance=capitulo_libro)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Capítulo de Libro', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Capítulo de Libro', None)])

    return render(request, 'cientifica/capitulo_libro/editar.html', locals())


@login_required
def capitulo_libro_eliminar(request, id):
    """
    Elimina un registro caputulo de libro, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    capitulo_libro = CapituloLibro.objects.get(id=id)
    capitulo_libro.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)

    return HttpResponseRedirect(next + '#tab_produccion_cientifica')


@login_required
def capitulo_libro_guardar(request, produccion_cientifica_id):
    """
    Crea o actualiza un registro de capitulo de libro, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        capitulo_libro = get_object_or_404(CapituloLibro, id=id)
    except:
        capitulo_libro = CapituloLibro()

    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    capitulo_libro_form = CapituloLibroForm(request.POST, instance=capitulo_libro)

    if capitulo_libro_form.is_valid():
        capitulo_libro = capitulo_libro_form.save(commit=False)
        capitulo_libro.produccion_cientifica = produccion_cientifica
        capitulo_libro.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_produccion_cientifica')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                           ('Capítulo de Libro', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (produccion_cientifica.expediente.persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[
                                        produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                           ('Capítulo de Libro', None)])

    return render(request, 'cientifica/capitulo_libro/editar.html', locals())


@login_required
def libro_crear(request, produccion_cientifica_id):
    """
    Muestra la interfaz para crear un libro  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.GET.get('next')
    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    libro_form = LibroForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Libro', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Libro', None)])

    return render(request, 'cientifica/libro/editar.html', locals())


@login_required
def libro_editar(request, id):
    """
    Muestra la interfaz para editar un libro  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    libro = Libro.objects.get(id=id)
    produccion_cientifica = libro.produccion_cientifica
    libro_form = LibroForm(instance=libro)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Libro', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Libro', None)])

    return render(request, 'cientifica/libro/editar.html', locals())


@login_required
def libro_eliminar(request, id):
    """
    Elimina un registro de libro, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    libro = Libro.objects.get(id=id)
    libro.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)

    return HttpResponseRedirect(next + '#tab_produccion_cientifica')


@login_required
def libro_guardar(request, produccion_cientifica_id):
    """
    Crea o actualiza un registro de libro, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        libro = get_object_or_404(Libro, id=id)
    except:
        libro = CapituloLibro()

    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    libro_form = LibroForm(request.POST, instance=libro)

    if libro_form.is_valid():
        libro = libro_form.save(commit=False)
        libro.produccion_cientifica = produccion_cientifica
        libro.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_produccion_cientifica')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                           ('Libro', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (produccion_cientifica.expediente.persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[
                                        produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                           ('Libro', None)])

    return render(request, 'cientifica/libro/editar.html', locals())


@login_required
def ponencia_crear(request, produccion_cientifica_id):
    """
    Muestra la interfaz para crear una ponencia  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.GET.get('next')
    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    ponencia_form = PonenciaForm()

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Ponencia', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Ponencia', None)])

    return render(request, 'cientifica/ponencia/editar.html', locals())


@login_required
def ponencia_editar(request, id):
    """
    Muestra la interfaz para editar una ponencia  y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    ponencia = Ponencia.objects.get(id=id)
    produccion_cientifica = ponencia.produccion_cientifica
    ponencia_form = PonenciaForm(instance=ponencia)

    if reverse('seguridad:usuario_perfil') == next:
        navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                      [('Inicio', reverse('index')),
                       ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                       ('Ponencia', None)])
    else:
        navegacion = ('Módulo de Talento Humano',
                      [('Talento Humano', reverse('talento_humano:index')),
                       ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                       (produccion_cientifica.expediente.persona.get_nombres_completos(),
                        reverse('talento_humano:funcionarios.funcionario',
                                args=[
                                    produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                       ('Ponencia', None)])

    return render(request, 'cientifica/ponencia/editar.html', locals())


@login_required
def ponencia_eliminar(request, id):
    """
    Elimina un registro de ponencia, y es invocado desde perfil y
    modificación de datos de funcionario.
    :param request:
    :param id:
    :return:
    """
    next = request.GET.get('next')
    ponencia = Ponencia.objects.get(id=id)
    ponencia.delete()
    messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)

    return HttpResponseRedirect(next + '#tab_produccion_cientifica')


@login_required
def ponencia_guardar(request, produccion_cientifica_id):
    """
    Crea o actualiza un registro de ponencia, y es invocado desde perfil y
    modificación de datos de funcionario
    :param request:
    :param produccion_cientifica_id:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        ponencia = get_object_or_404(Ponencia, id=id)
    except:
        ponencia = Ponencia()

    produccion_cientifica = ProduccionCientifica.objects.get(id=produccion_cientifica_id)
    ponencia_form = PonenciaForm(request.POST, instance=ponencia)

    if ponencia_form.is_valid():
        ponencia = ponencia_form.save(commit=False)
        ponencia.produccion_cientifica = produccion_cientifica
        ponencia.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
        return HttpResponseRedirect(next + '#tab_produccion_cientifica')
    else:
        messages.warning(request, MensajesEnum.DATOS_INCOMPLETOS.value)
        if reverse('seguridad:usuario_perfil') == next:
            navegacion = ('Perfil de %s' % produccion_cientifica.expediente.persona.get_nombres_completos(),
                          [('Inicio', reverse('index')),
                           ('Perfil', reverse('seguridad:usuario_perfil') + '#tab_produccion_cientifica'),
                           ('Ponencia', None)])
        else:
            navegacion = ('Módulo de Talento Humano',
                          [('Talento Humano', reverse('talento_humano:index')),
                           ('Gestión de Funcionarios', reverse('talento_humano:funcionarios.index')),
                           (produccion_cientifica.expediente.persona.get_nombres_completos(),
                            reverse('talento_humano:funcionarios.funcionario',
                                    args=[
                                        produccion_cientifica.expediente.persona.usuario.funcionario.id]) + '#tab_produccion_cientifica'),
                           ('Ponencia', None)])

    return render(request, 'cientifica/ponencia/editar.html', locals())


@login_required
def produccion_cientifica_crear(request, persona_id):
    """
    Crea un registro de producción cientifica a la persona a fin de poder crear articulos, ponencia
    libros y capitulos de libros.
    :param request:
    :param persona_id:
    :return:
    """
    next = request.GET.get('next')
    persona = Persona.objects.get(id=persona_id)

    try:
        expediente = persona.expediente
    except:
        expediente = Expediente()
        expediente.persona = persona
        expediente.save()
    try:
        expediente.produccioncientifica
    except:
        produccion_cientifica = ProduccionCientifica()
        produccion_cientifica.expediente = expediente
        produccion_cientifica.save()

    return HttpResponseRedirect(next + '#tab_produccion_cientifica')
