from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponse
from django.http import HttpResponseServerError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user

from app.academico.forms import AsignaturaForm
from app.academico.forms import AsignaturaNivelCorrequisitoForm
from app.academico.forms import AsignaturaNivelForm
from app.academico.forms import AsignaturaNivelPrerrequisitoForm
from app.academico.forms import AutoridadFacultadForm
from app.academico.forms import AutoridadProgramaEstudioForm
from app.academico.forms import FacultadForm
from app.academico.forms import NivelForm
from app.academico.forms import PensumComplementarioForm
from app.academico.forms import PensumForm
from app.academico.forms import PensumPensumGrupoForm
from app.academico.forms import PensumGrupoForm
from app.academico.forms import ProgramaEstudioForm
from app.academico.forms import TituloForm
from app.academico.models import Asignatura
from app.academico.models import AsignaturaComponente
from app.academico.models import AsignaturaNivel
from app.academico.models import AutoridadFacultad
from app.academico.models import AutoridadProgramaEstudio
from app.academico.models import CampoDetallado
from app.academico.models import OfertaAcademica
from app.academico.models import Facultad
from app.academico.models import Nivel
from app.academico.models import NivelFormacion
from app.academico.models import Pensum
from app.academico.models import PensumComplementario
from app.academico.models import PensumGrupo
from app.academico.models import ProgramaEstudio
from app.academico.models import TipoFormacion
from app.academico.models import Titulo
from app.academico import models
from app.academico.utils.datatable import DatatableBuscar
from app.core.dto.datatable import DataTableParams
from app.core.utils.enums import MensajesEnum
from app.talento_humano.models import Funcionario


@login_required
def index_curricular(request):
    """
    Index de la sección curricular del académico
    :param request:
    :return:
    """
    navegacion = ('Módulo académico',
                  [('Curricular', reverse('academico:index_curricular'))])
    return render(request, 'academico/index_curricular.html', locals())


@login_required
@require_http_methods(["POST"])
def asignatura_componente_guardar(request):
    """
    Metodo para actualizar un componente (ajax)
    :param request: {datos en json}
    :return:
    """
    # asignatura_componente solo viene por ajax
    if request.method == 'POST' and request.is_ajax() and request.POST.get('id', False):

        asignatura_componente = get_object_or_404(AsignaturaComponente, id=request.POST.get('id', False))
        if not (request.user.has_perm("academico.change_asignaturacomponente") or
                request.user.has_perm("academico.change_asignaturacomponente", asignatura_componente)):
            raise PermissionDenied
        asignatura_componente.duracion = request.POST.get('duracion', 0)
        asignatura_componente.save()
        return JsonResponse({'asignatura_duracion': asignatura_componente.asignatura_nivel.duracion})
    return HttpResponseBadRequest('Metodo no valido')


@login_required
@permission_required_or_403('academico.view_asignaturanivel',(AsignaturaNivel, 'id', 'id'), accept_global_perms=True)
def asignatura_nivel_detalle(request, id):
    """
    Muestra el detalle de una asignatura del pensum con sus acciones
    :param request:
    :param id:
    :return:
    """
    asignatura_nivel = get_object_or_404(AsignaturaNivel, id=id)
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   (asignatura_nivel.nivel.pensum.programa_estudio.nombre, reverse('academico:programa_estudio_detalle',
                                                                                   kwargs={
                                                                                       'id': asignatura_nivel.nivel.pensum.programa_estudio.id})),
                   ('Pensum %s' % asignatura_nivel.nivel.pensum.nombre,
                    reverse('academico:pensum_detalle', kwargs={'id': asignatura_nivel.nivel.pensum.id})),
                   ("%s %s" % (asignatura_nivel.nivel.pensum.get_organizacion_display(), asignatura_nivel.nivel),
                    reverse('academico:nivel_detalle', kwargs={'id': asignatura_nivel.nivel.id})),
                   ('Asignatura', None)])

    asignaturas = Asignatura.objects.values('id', 'codigo_institucional', 'nombre')
    campos_formacion = asignatura_nivel.nivel.pensum.programa_estudio.get_campos_formacion()
    CHOICE_TIPO = AsignaturaNivel.CHOICE_TIPO
    correquisitos_values = asignatura_nivel.nivel.asignaturas.exclude(
        id=asignatura_nivel.id).values('id',
                                       'asignatura__nombre',
                                       'nivel__numero')
    prerrequisitos_values = asignatura_nivel.nivel.get_prerrequisitos_posibles().values('id', 'asignatura__nombre',
                                                                                        'nivel__numero')
    return render(request, 'academico/asignatura_nivel/detalle.html', locals())


@login_required
@permission_required_or_403('academico.delete_asignaturanivel',(AsignaturaNivel, 'id', 'id'), accept_global_perms=True)
def asignatura_nivel_eliminar(request, id):
    """
    Elimina un registro de asignatura del pensum
    :param request:
    :param id:
    :return:
    """
    asignatura_nivel = get_object_or_404(AsignaturaNivel, id=id)
    if asignatura_nivel.delete():
        messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
        return redirect('academico:nivel_detalle', asignatura_nivel.nivel.id)
    else:
        messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
        return redirect('academico:asignatura_nivel_detalle', id)


@login_required
@require_http_methods(["POST"])
def asignatura_nivel_guardar(request):
    """
    Guarda una nueva asignatura o actualiza
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        asignatura_nivel = get_object_or_404(AsignaturaNivel, id=id)
        if not (request.user.has_perm("academico.change_asignaturanivel") or
                request.user.has_perm("academico.change_asignaturanivel", asignatura_nivel)):
            raise PermissionDenied
    else:
        asignatura_nivel = AsignaturaNivel()

    form = AsignaturaNivelForm(request.POST, instance=asignatura_nivel)
    if form.is_valid():
        if not id and not (request.user.has_perm("academico.add_asignaturanivel") or
                           request.user.has_perm("academico.add_asignaturanivel", form.cleaned_data.get('nivel'))):
            raise PermissionDenied
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    return redirect('academico:index_curricular', )


@login_required
@require_http_methods(["POST"])
def asignatura_nivel_guardar_prerrequisito(request):
    """
    Actualiza prerrequisitos y correquisitos
    :param request:
    :return:
    """
    asignatura_nivel = get_object_or_404(AsignaturaNivel, id=request.POST.get('id'))
    if not (request.user.has_perm('academico.change_asignaturanivel') or request.user.has_perm('academico.change_asignaturanivel', asignatura_nivel)):
        raise PermissionDenied
    asignatura_form = AsignaturaNivelPrerrequisitoForm(request.POST, instance=asignatura_nivel)
    if asignatura_form.is_valid():
        asignatura_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, asignatura_form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    return redirect('academico:asignatura_nivel_detalle', asignatura_nivel.id)


@login_required
@require_http_methods(["POST"])
def asignatura_nivel_guardar_correquisito(request):
    """
    Actualiza prerrequisitos y correquisitos
    :param request:
    :return:
    """
    asignatura_nivel = get_object_or_404(AsignaturaNivel, id=request.POST.get('id'))
    if not (request.user.has_perm('academico.change_asignaturanivel') or request.user.has_perm('academico.change_asignaturanivel', asignatura_nivel)):
        raise PermissionDenied
    asignatura_form = AsignaturaNivelCorrequisitoForm(request.POST, instance=asignatura_nivel)
    if asignatura_form.is_valid():
        asignatura_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, asignatura_form.errors)
    return redirect('academico:asignatura_nivel_detalle', asignatura_nivel.id)


@login_required
@permission_required('academico.view_asignatura', raise_exception=True, )
def asignatura_detalle(request, id):
    """
    Muestra el detalle de una asignatura con sus acciones
    :param request:
    :param id:
    :return:
    """
    asignatura = get_object_or_404(Asignatura, id=id)

    CHOICE_TIPO = Asignatura.CHOICE_TIPO

    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Asignaturas', reverse('academico:asignatura_lista')),
                   (asignatura.nombre, None)])

    return render(request, 'academico/asignatura/detalle.html', locals())


@login_required
@permission_required('academico.delete_asignatura', raise_exception=True, )
def asignatura_eliminar(request, id):
    """
    Elimina un registro de asignatura
    :param request:
    :param id:
    :return:
    """
    asignatura = get_object_or_404(Asignatura, id=id)
    try:
        if asignatura.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:asignatura_lista')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:asignatura_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('academico.change_asignatura', raise_exception=True, )
@require_http_methods(["POST"])
def asignatura_guardar(request):
    """
    Guarda una nueva asignatura o actualiza
    :param request:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        asignatura = get_object_or_404(Asignatura, id=id)
    except:
        asignatura = Asignatura()

    asignatura_form = AsignaturaForm(request.POST, instance=asignatura)
    if asignatura_form.is_valid():
        asignatura_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, asignatura_form.errors)

    return redirect(next)


@login_required
@permission_required('academico.view_asignatura', raise_exception=True, )
def asignatura_lista(request):
    """
    Lista las asignaturas
    :param request:
    :return:
    """
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Asignaturas', None)])

    CHOICE_TIPO = Asignatura.CHOICE_TIPO

    return render(request, 'academico/asignatura/lista.html', locals())


@login_required
@permission_required('academico.view_asignatura', raise_exception=True, )
@require_http_methods(["POST"])
def asignatura_lista_paginador(request):
    """
    Lista las asignaturas con la paginación de datatable
    :param request:
    :return:
    """
    try:
        params = DataTableParams(request, **request.POST)
        DatatableBuscar.asignatura(params)
        data = params.items.values('id', 'nombre','codigo_unesco', 'tipo').all()
        result = params.result(list(data))
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseServerError(e)

@login_required
@permission_required('academico.view_autoridadfacultad', raise_exception=True, )
@require_http_methods(["GET"])
def autoridad_facultad_detalle(request, id):
    """
    Muestra la interfaz con el detalle de la autoridad
    :param request:
    :param id:
    :return:
    """
    autoridad_facultad = get_object_or_404(AutoridadFacultad, id=id)
    funcionarios = Funcionario.objects.filter(activo=True).values('id',
                                                                  'usuario__persona__primer_nombre',
                                                                  'usuario__persona__segundo_nombre',
                                                                  'usuario__persona__primer_apellido',
                                                                  'usuario__persona__segundo_apellido')

    CHOICE_TIPO_AUTORIDAD = AutoridadFacultad.CHOICE_TIPO
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Facultades', reverse('academico:facultad_lista')),
                   (autoridad_facultad.facultad.siglas,
                    reverse('academico:facultad_detalle', args=[autoridad_facultad.facultad.id])),
                   ('Autoridad académica', None)
                   ])

    return render(request, 'academico/autoridad_facultad/detalle.html', locals())

@login_required
@permission_required('academico.delete_autoridadfacultad', raise_exception=True, )
@require_http_methods(["GET"])
def autoridad_facultad_eliminar(request, id):
    """
    Elimina un registro de autoridad
    :param request:
    :param id:
    :return:
    """
    autoridad_facultad = get_object_or_404(AutoridadFacultad, id=id)
    try:
        if autoridad_facultad.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:facultad_detalle', autoridad_facultad.facultad_id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:autoridad_facultad_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))

@login_required
@permission_required('academico.change_autoridadfacultad', raise_exception=True, )
@require_http_methods(["POST"])
def autoridad_facultad_guardar(request):
    """
    Guarda o actualiza un registro de autoridad
    :param request:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        autoridad_facultad = get_object_or_404(AutoridadFacultad, id=id)
    except:
        autoridad_facultad = AutoridadFacultad()

    autoridad_facultad_form = AutoridadFacultadForm(request.POST, instance=autoridad_facultad)
    if autoridad_facultad_form.is_valid():
        autoridad_facultad.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, autoridad_facultad_form.errors)

    return redirect(next)


@login_required
@permission_required('academico.view_autoridadprogramaestudio', raise_exception=True, )
@require_http_methods(["GET"])
def autoridad_programa_estudio_detalle(request, id):
    """
    Muestra la interfaz con el detalle de la autoridad
    :param request:
    :param id:
    :return:
    """
    autoridad_programa_estudio = get_object_or_404(AutoridadProgramaEstudio, id=id)
    funcionarios = Funcionario.objects.filter(activo=True).values('id',
                                                                  'usuario__persona__primer_nombre',
                                                                  'usuario__persona__segundo_nombre',
                                                                  'usuario__persona__primer_apellido',
                                                                  'usuario__persona__segundo_apellido')

    CHOICE_TIPO_AUTORIDAD = AutoridadProgramaEstudio.CHOICE_TIPO
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Programas de estudio', reverse('academico:programa_estudio_lista')),
                   (autoridad_programa_estudio.programa_estudio.nombre,
                    reverse('academico:programa_estudio_detalle', args=[autoridad_programa_estudio.programa_estudio.id])),
                   ('Autoridad académica', None)
                   ])

    return render(request, 'academico/autoridad_programa_estudio/detalle.html', locals())


@login_required
@permission_required('academico.delete_autoridadprogramaestudio', raise_exception=True, )
@require_http_methods(["GET"])
def autoridad_programa_estudio_eliminar(request, id):
    """
    Elimina un registro de autoridad académica
    :param request:
    :param id:
    :return:
    """
    autoridad_programa_estudio = get_object_or_404(AutoridadProgramaEstudio, id=id)
    try:
        if autoridad_programa_estudio.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:programa_estudio_detalle', autoridad_programa_estudio.programa_estudio_id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:autoridad_programa_estudio_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('academico.change_autoridadprogramaestudio', raise_exception=True, )
@require_http_methods(["POST"])
def autoridad_programa_estudio_guardar(request):
    """
    Guarda o actualiza un nuevo registro de autoridad
    :param request:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')

    try:
        autoridad_programa_estudio = get_object_or_404(AutoridadProgramaEstudio, id=id)
    except:
        autoridad_programa_estudio = AutoridadProgramaEstudio()

    autoridad_programa_estudio_form = AutoridadProgramaEstudioForm(request.POST, instance=autoridad_programa_estudio)
    if autoridad_programa_estudio_form.is_valid():
        autoridad_programa_estudio_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, autoridad_programa_estudio_form.errors)

    return redirect(next)

@login_required
@permission_required('academico.view_facultad', raise_exception=True, )
def facultad_detalle(request, id):
    """
    Muestra el detalle de una Facultad
    :param request:
    :param id: id de la Facultad
    :return:
    """
    facultad = get_object_or_404(Facultad, id=id)
    # Referente a autoridad academica
    CHOICE_TIPO_AUTORIDAD = AutoridadFacultad.CHOICE_TIPO
    funcionarios = Funcionario.objects.filter(activo=True).values('id',
                                                                  'usuario__persona__primer_nombre',
                                                                  'usuario__persona__segundo_nombre',
                                                                  'usuario__persona__primer_apellido',
                                                                  'usuario__persona__segundo_apellido')

    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Facultades', reverse('academico:facultad_lista')),
                   (facultad.nombre, None)])
    return render(request, 'academico/facultad/detalle.html', locals())


@login_required
@permission_required('academico.view_facultad', raise_exception=True, )
def facultad_lista(request):
    """
    Lista las Facultades
    :param request:
    :return:
    """
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Facultad', None)])
    facultades = Facultad.objects.all()
    return render(request, 'academico/facultad/lista.html', locals())


@login_required
@permission_required_or_403('academico.view_nivel',(Nivel, 'id', 'id'), accept_global_perms=True)
def nivel_detalle(request, id):
    """
    Muestra el detalle de un nivel del pensum
    :param request:
    :param id:
    :return:
    """
    nivel = get_object_or_404(Nivel, id=id)
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   (nivel.pensum.programa_estudio.nombre, reverse('academico:programa_estudio_detalle',
                                                                  kwargs={'id': nivel.pensum.programa_estudio.id})),
                   ('Pensum %s' % nivel.pensum.nombre,
                    reverse('academico:pensum_detalle', kwargs={'id': nivel.pensum.id})),
                   ('Nivel', None)])
    organizaciones_curricular = nivel.pensum.programa_estudio.get_organizaciones_curriculares()
    asignaturas = Asignatura.objects.exclude(asignaturas_nivel__nivel__pensum=nivel.pensum).values('id',
                                                                                                   'codigo_institucional',
                                                                                                   'nombre')
    campos_formacion = nivel.pensum.programa_estudio.get_campos_formacion()
    CHOICE_TIPO = AsignaturaNivel.CHOICE_TIPO
    return render(request, 'academico/nivel/detalle.html', locals())

@login_required
@permission_required_or_403('academico.delete_nivel',(Nivel, 'id', 'id'), accept_global_perms=True)
def nivel_eliminar(request, id):
    """
     Elimina un nivel del pensum
    :param request:
    :param id:
    :return:
    """
    nivel = get_object_or_404(Nivel, id=id)
    if nivel.delete():
        messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
        return redirect('academico:pensum_detalle', nivel.pensum.id)
    else:
        messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
        return redirect('academico:nivel_detalle', id)


@login_required
@require_http_methods(["POST"])
def nivel_guardar(request):
    """
    Guarda o actualiza un nivel del pensum
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        nivel = get_object_or_404(Nivel, id=id)
        if not (request.user.has_perm("academico.change_nivel") or request.user.has_perm("academico.change_nivel",
                                                                                          nivel)):
            raise PermissionDenied
    else:
        nivel = Nivel()

    form = NivelForm(request.POST, instance=nivel)
    if form.is_valid():
        if not id and not (request.user.has_perm("academico.add_nivel") or
                           request.user.has_perm("academico.add_nivel", form.cleaned_data.get('pensum'))):
            messages.warning(request, "No puede crear niveles en el pensum")
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)

    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:nivel_detalle', id)

    return redirect('academico:index_curricular')


@login_required
@permission_required('academico.change_facultad', raise_exception=True, )
@require_http_methods(["POST"])
def facultad_guardar(request):
    """
    Guarda un registro de Facultad
    :param request:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')
    try:
        facultad = get_object_or_404(Facultad, id=id)
    except:
        facultad = Facultad()
    facultad_form = FacultadForm(request.POST, instance=facultad)
    if facultad_form.is_valid():
        facultad_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, facultad_form.errors)
    return redirect(next)


@login_required
@permission_required('academico.delete_facultad', raise_exception=True, )
def facultad_eliminar(request, id):
    """
    Elimina un registro de Facultad
    :param request:
    :param id: id de la Facultad
    :return:
    """
    facultad = get_object_or_404(Facultad, id=id)
    try:
        if facultad.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:facultad_lista')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:facultad_detalle', id)
    except Facultad.DoesNotExist:
        HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required_or_403('academico.view_pensum',(Pensum, 'id', 'id'), accept_global_perms=True)
def pensum_detalle(request, id):
    """
    Muestra el detalle del pensum, incluido los titulos que tenga
    :param request:
    :param id:
    :return:
    """
    pensum = get_object_or_404(Pensum, id=id)
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   (pensum.programa_estudio.nombre, reverse('academico:programa_estudio_detalle',
                                                            kwargs={'id': pensum.programa_estudio.id})),
                   (pensum.nombre, None)])
    # Para el pensum
    CHOICE_ORGANIZACION = Pensum.CHOICE_ORGANIZACION
    CHOICE_DURACION_UNIDAD = Pensum.CHOICE_DURACION_UNIDAD
    CHOICE_TIPO_PENSUM = Pensum.CHOICE_TIPO
    TIPO_CURSO_APOYO = ProgramaEstudio.TIPO_CURSO_APOYO
    pensums_grupo = PensumGrupo.objects.all()
    # Para el nivel
    organizaciones_curricular = pensum.programa_estudio.get_organizaciones_curriculares()
    return render(request, 'academico/pensum/detalle.html', locals())


@login_required
@permission_required_or_403('academico.delete_pensum',(Pensum, 'id', 'id'), accept_global_perms=True)
def pensum_eliminar(request, id):
    """
    Elimina el pensum pasado por id (GET)
    :param request:
    :param id:
    :return:
    """
    pensum = get_object_or_404(Pensum, id=id)
    try:
        if pensum.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:programa_estudio_detalle', pensum.programa_estudio.id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:pensum_detalle', id)
    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@require_http_methods(["POST"])
def pensum_guardar(request):
    """
    Crea o actualiza un pensum desde su modal-pensum-editar
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        pensum = Pensum.objects.get(id=id)
        if not (request.user.has_perm("academico.change_pensum") or request.user.has_perm("academico.change_pensum", pensum)):
            raise PermissionDenied
    else:
        pensum = Pensum()

    form = PensumForm(request.POST, instance=pensum)
    if form.is_valid():
        if not id and not (request.user.has_perm("academico.add_pensum", form.cleaned_data.get('programa_estudio'))
                           or request.user.has_perm("academico.add_pensum")):
            messages.warning(request, "No puede crear pensums en la carrera")
            raise PermissionDenied
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:pensum_detalle', id)
    return redirect(reverse('academico:index_curricular', ))

@login_required
@require_http_methods(["POST"])
def pensum_guardar_pensums_grupo(request):
    """
    Actualiza grupos de pensums complementarios
    :param request:
    :return:
    """
    pensum = get_object_or_404(Pensum, id=request.POST.get('id'))
    if not (request.user.has_perm('academico.change_pensum') or request.user.has_perm('academico.change_pensum', pensum)):
        raise PermissionDenied
    pensum_form = PensumPensumGrupoForm(request.POST, instance=pensum)
    if pensum_form.is_valid():
        pensum_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, pensum_form.errors)
    url = reverse('academico:pensum_detalle', kwargs={'id':pensum.id})
    return redirect(url+'?#card_complementarios')

@login_required
def pensum_lista(request):
    """
    Lista todos los pensums
    :param request:
    :return:
    """
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Pensum', None)])
    pensums = get_objects_for_user(request.user, 'academico.view_pensum', accept_global_perms=True)
    CHOICE_ORGANIZACION = Pensum.CHOICE_ORGANIZACION
    CHOICE_DURACION_UNIDAD = Pensum.CHOICE_DURACION_UNIDAD
    return render(request, 'academico/pensum/lista.html', locals())


@login_required
@permission_required('academico.delete_pensumcomplementario', raise_exception=True, )
def pensum_complementario_eliminar(request, id):
    """
    Elimina el pensum pasado por id (GET)
    :param request:
    :param id:
    :return:
    """
    pensum_complementario = get_object_or_404(PensumComplementario, id=id)
    try:
        if pensum_complementario.delete():

            pensum_grupo = pensum_complementario.pensum_grupo
            if not pensum_grupo.pensums_complementarios.filter(tipo=PensumComplementario.TIPO_OPTATIVO).all():
                pensum_grupo.nro_optativo_obligatorios = 0
                pensum_grupo.save()

            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:pensum_grupo_detalle', pensum_complementario.pensum_grupo.id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:pensum_complementario_detalle', id)
    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('academico.change_pensumcomplementario', raise_exception=True, )
@require_http_methods(["POST"])
def pensum_complementario_guardar(request):
    """
    Crea o actualiza un pensum desde su modal-pensum-editar
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        pensum_complementario = PensumComplementario.objects.get(id=id)
    else:
        pensum_complementario = PensumComplementario()
    form = PensumComplementarioForm(request.POST, instance=pensum_complementario)
    if form.is_valid():
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:pensum_complementario_detalle', id)
    return redirect(reverse('academico:index_curricular', ))


@login_required
@permission_required('academico.view_pensumgrupo', raise_exception=True, )
def pensum_grupo_detalle(request, id):
    """
    Muestra el detalle del pensumgrupo, incluido los pensums que tenga
    :param request:
    :param id:
    :return:
    """
    pensum_grupo = get_object_or_404(PensumGrupo, id=id)
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Agrupaciones de pensums', reverse('academico:pensum_grupo_lista')),
                   (pensum_grupo.nombre, None)])
    # Para el pensumcomplementario
    deshabilitar = 'readonly'
    CHOICE_TIPO = PensumComplementario.CHOICE_TIPO
    TIPO_OBLIGATORIO = PensumComplementario.TIPO_OBLIGATORIO
    nro_optativos = pensum_grupo.pensums_complementarios.filter(tipo=PensumComplementario.TIPO_OPTATIVO).count()
    pensums = Pensum.objects.filter(programa_estudio__tipo=ProgramaEstudio.TIPO_CURSO_APOYO).exclude(
                                    pensums_complementarios__pensum_grupo=pensum_grupo).all()
    return render(request, 'academico/pensum_grupo/detalle.html', locals())


@login_required
@permission_required('academico.delete_pensumgrupo', raise_exception=True, )
def pensum_grupo_eliminar(request, id):
    """
    Elimina el pensum pasado por id (GET)
    :param request:
    :param id:
    :return:
    """
    pensum_grupo = get_object_or_404(PensumGrupo, id=id)
    try:
        if pensum_grupo.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:pensum_grupo_lista', )
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:pensum_grupo_detalle', id)
    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('academico.change_pensumgrupo', raise_exception=True, )
@require_http_methods(["POST"])
def pensum_grupo_guardar(request):
    """
    Crea o actualiza un pensum desde su modal-pensum-editar
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        pensum_grupo = PensumGrupo.objects.get(id=id)
    else:
        pensum_grupo = PensumGrupo()
    form = PensumGrupoForm(request.POST, instance=pensum_grupo)
    if form.is_valid():
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:pensum_grupo_detalle', id)
    return redirect(reverse('academico:index_curricular', ))


@login_required
@permission_required('academico.view_pensumgrupo', raise_exception=True, )
def pensum_grupo_lista(request):
    """
    Lista todos los pensums
    :param request:
    :return:
    """
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Agrupaciones de pensums', None)])
    pensums_grupo = PensumGrupo.objects.all()
    return render(request, 'academico/pensum_grupo/lista.html', locals())



@login_required
@permission_required_or_403('academico.view_programaestudio', (ProgramaEstudio, 'id', 'id'), accept_global_perms=True,)
def programa_estudio_detalle(request, id):
    """
    Muestra el detalle de un programa de estudio con su lista de autoridades academicas y pensums
    :param request:
    :param id:
    :return:
    """
    programa_estudio = get_object_or_404(ProgramaEstudio, id=id)

    # Referente a programa de estudio
    CHOICE_ESTADO = programa_estudio.CHOICE_ESTADO
    CHOICE_MODALIDAD = programa_estudio.CHOICE_MODALIDAD
    CHOICE_TIPO = programa_estudio.CHOICE_TIPO
    CHOICE_REGIMEN = models.CHOICE_REGIMEN
    TIPO_CURSO_APOYO = programa_estudio.TIPO_CURSO_APOYO
    campos_detallado = CampoDetallado.objects.all().order_by('campo_especifico__campo_amplio__nombre')
    facultades = Facultad.objects.all().order_by('siglas')


    # Referente a autoridad academica
    CHOICE_TIPO_AUTORIDAD = AutoridadProgramaEstudio.CHOICE_TIPO
    funcionarios = Funcionario.objects.filter(activo=True).values('id',
                                                                  'usuario__persona__primer_nombre',
                                                                  'usuario__persona__segundo_nombre',
                                                                  'usuario__persona__primer_apellido',
                                                                  'usuario__persona__segundo_apellido')
    # Referente al pensum
    CHOICE_ORGANIZACION = Pensum.CHOICE_ORGANIZACION
    CHOICE_DURACION_UNIDAD = Pensum.CHOICE_DURACION_UNIDAD
    CHOICE_TIPO_PENSUM = Pensum.CHOICE_TIPO

    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Programas de estudio', reverse('academico:programa_estudio_lista')),
                   (programa_estudio.nombre, None)])

    return render(request, 'academico/programa_estudio/detalle.html', locals())


@login_required
@permission_required_or_403('academico.delete_programaestudio', (ProgramaEstudio, 'id', 'id'), accept_global_perms=True)
def programa_estudio_eliminar(request, id):
    """
    Elimina un registro del programa de estudio
    :param request:
    :param id:
    :return:
    """
    programa_estudio = get_object_or_404(ProgramaEstudio, id=id)
    try:
        if programa_estudio.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:programa_estudio_lista')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:programa_estudio_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@require_http_methods(['POST'])
def programa_estudio_guardar(request):
    """
    Guarda un nuevo programa de estudio o actualiza
    :param request:
    :return:
    """
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        programa_estudio = get_object_or_404(ProgramaEstudio, id=id)
        if not (request.user.has_perm("academico.change_programaestudio") or request.user.has_perm("academico.change_programaestudio", programa_estudio)):
            raise PermissionDenied
    else:
        if not request.user.has_perm("academico.add_programaestudio"):
            raise PermissionDenied
        programa_estudio = ProgramaEstudio()

    programa_estudio_form = ProgramaEstudioForm(request.POST, instance=programa_estudio)
    if programa_estudio_form.is_valid():
        programa_estudio_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, programa_estudio_form.errors)

    return redirect(next)


@login_required
def programa_estudio_lista(request):
    """
    Lista los programas de estudio
    :param request:
    :return:
    """
    CHOICE_ESTADO = ProgramaEstudio.CHOICE_ESTADO
    CHOICE_MODALIDAD = ProgramaEstudio.CHOICE_MODALIDAD
    CHOICE_TIPO = ProgramaEstudio.CHOICE_TIPO
    CHOICE_REGIMEN = models.CHOICE_REGIMEN
    TIPO_CURSO_APOYO = ProgramaEstudio.TIPO_CURSO_APOYO

    campos_detallado = CampoDetallado.objects.all().order_by('campo_especifico__campo_amplio__nombre')
    facultades = Facultad.objects.all().order_by('siglas')

    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Programas de estudio', None)])

    return render(request, 'academico/programa_estudio/lista.html', locals())


@login_required
@require_http_methods(["POST"])
def programa_estudio_lista_paginador(request):
    """
    Lista los programas de estudio con la paginación de datatable
    :param request:
    :return:
    """
    try:
        params = DataTableParams(request, **request.POST)
        DatatableBuscar.programa_estudio(params)
        data = [{
            'id': it.id,
            'nombre': it.nombre,
            'modalidad': it.get_modalidad_display(),
            'facultad': it.facultad.siglas} for it in
            params.items]
        result = params.result(data)
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseServerError(e)


@login_required
@permission_required_or_403('academico.view_programaestudio',(ProgramaEstudio, 'id', 'id'), accept_global_perms=True)
def programa_estudio_detalle_perfil(request, id):
    """
    Muestra el detalle de un programa de estudio con su lista de autoridades academicas y pensums
    :param request:
    :param id:
    :return:
    """
    try:
        programa_estudio = ProgramaEstudio.objects.get(id=id)
        navegacion = ('Módulo Académico',
                      [('Curricular', reverse('academico:index_curricular')),
                       ('Programas de estudio', reverse('academico:programa_estudio_lista_perfil')),
                       (programa_estudio.nombre, None)])
        ofertas_academicas = OfertaAcademica.objects.filter(ofertas_pensum__pensum__programa_estudio=programa_estudio)
        return render(request, 'academico/programa_estudio/detalle_perfil.html', locals())
    except ProgramaEstudio.DoesNotExist:
        return HttpResponseServerError(render(request, '404.html'))

@login_required
def programa_estudio_lista_perfil(request):
    """
    Lista los programas de estudio
    :param request:
    :return:
    """
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   ('Programas de estudio', None)])
    programas_estudio = get_objects_for_user(request.user, 'academico.view_programaestudio', accept_global_perms=True)
    return render(request, 'academico/programa_estudio/lista_perfil.html', locals())

@login_required
@permission_required('academico.view_titulo', raise_exception=True, )
def titulo_detalle(request, id):
    """
    Muestra el detalle de un titulo de pensum
    :param request:
    :param id:
    :return:
    """
    titulo = get_object_or_404(Titulo, id=id)
    navegacion = ('Módulo Académico',
                  [('Curricular', reverse('academico:index_curricular')),
                   (titulo.pensum.programa_estudio.nombre, reverse('academico:programa_estudio_detalle',
                                                                   kwargs={'id': titulo.pensum.programa_estudio.id})),
                   ('Pensum %s' % titulo.pensum.nombre, reverse('academico:pensum_detalle',
                                                                  kwargs={'id': titulo.pensum.id})),
                   ('Titulo', None)])

    return render(request, 'academico/titulo/detalle.html', locals())


@login_required
@permission_required('academico.delete_titulo', raise_exception=True, )
def titulo_eliminar(request, id):
    """
    elimina el titulo de un pensum
    :param request:
    :param id:
    :return:
    """
    titulo = get_object_or_404(Titulo, id=id)
    try:
        if titulo.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:pensum_detalle', titulo.pensum.id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('academico:titulo_detalle', id)
    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('academico.change_titulo', raise_exception=True, )
@require_http_methods(["POST"])
def titulo_guardar(request):
    """
    Guarda o actualiza un titulo
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        titulo = Titulo.objects.get(id=id)
    else:
        titulo = Titulo()
    form = TituloForm(request.POST, instance=titulo)
    if form.is_valid():
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:titulo_detalle', id)
    return redirect(reverse('academico:index_curricular', ))


@login_required
@require_http_methods(["GET"])
def tipo_formacion(request, regimen):
    """
    Lista de tipos de formación de acuerdo al regimen
    :param request:
    :return:
    """
    data = []
    tipos_formacion = TipoFormacion.objects.filter(nivel_formacion__regimen=regimen, nivel_formacion__estado=NivelFormacion.ESTADO_ACTIVO)
    for tipo_formacion in tipos_formacion:
        item = {'id': tipo_formacion.id,
                'nombre': tipo_formacion.nombre,
                'display_nombre': '%s - %s' % (tipo_formacion.nivel_formacion.nombre, tipo_formacion.nombre)}
        data.append(item)
    return JsonResponse(data, safe=False)
