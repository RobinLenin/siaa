from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from guardian.decorators import permission_required_or_403

from app.academico.forms import OfertaAcademicaForm
from app.academico.forms import OfertaAsignaturaNivelForm
from app.academico.forms import OfertaPensumForm
from app.academico.forms import PeriodoAcademicoForm
from app.academico.forms import PeriodoMariculaForm
from app.academico.models import OfertaAsignaturaNivel
from app.academico.models import OfertaPensum
from app.academico.models import OfertaAcademica
from app.academico.models import ProgramaEstudio
from app.academico.models import PeriodoAcademico
from app.academico.models import PeriodoMatricula
from app.core.models import CatalogoItem
from app.core.utils.enums import MensajesEnum

@login_required
@permission_required('academico.view_ofertaacademica')
def oferta_academica_detalle(request, id):
    """
    Muestra el detalle de una Oferta Academica
    :param request:
    :param id:
    :return:
    """
    oferta_academica = get_object_or_404(OfertaAcademica, id=id)

    # CHOICE para oferta académica
    CHOICE_ESTADO = OfertaAcademica.CHOICE_ESTADO
    # CHOICE para el periodo academico
    CHOICE_TIPO = PeriodoMatricula.CHOICE_TIPO

    navegacion = ('Módulo académico',
                  [('Periódos académicos', reverse('academico:periodo_academico_lista')),
                   (oferta_academica.periodo_academico.nombre, reverse('academico:periodo_academico_detalle',
                                                                       kwargs={
                                                                           'id': oferta_academica.periodo_academico.id})),
                   ('Oferta académica', None)])
    programas_estudio = ProgramaEstudio.objects.all()
    pensums_ofertados_ids = [op.pensum.id for op in oferta_academica.ofertas_pensum.all()]
    return render(request, 'academico/oferta_academica/detalle.html', locals())


@login_required
@permission_required('academico.delete_ofertaacademica')
def oferta_academica_eliminar(request, id):
    """
     Elimina una oferta academica
    :param request:
    :param id:
    :return:
    """
    oferta_academica = get_object_or_404(OfertaAcademica, id=id)

    if oferta_academica.delete():
        messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
        return redirect('academico:periodo_academico_detalle', oferta_academica.periodo_academico.id)
    else:
        messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
        return redirect('academico:oferta_academica_detalle', id)


@login_required
@require_http_methods(["POST"])
def oferta_academica_guardar(request):
    """
    Guarda o actualiza una oferta académica
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        oferta_academica = get_object_or_404(OfertaAcademica, id=id)
    else:
        oferta_academica = OfertaAcademica()
    form = OfertaAcademicaForm(request.POST, instance=oferta_academica)
    if form.is_valid():
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:oferta_academica_detalle', id)
    return redirect(reverse('academico:periodo_academico/lista', ))

@login_required
@permission_required_or_403('academico.delete_ofertaasignaturanivel', (OfertaAsignaturaNivel, 'id', 'id'),
                            accept_global_perms=True, )
@require_http_methods(["DELETE"])
def oferta_asignatura_nivel_eliminar(request, id):
    """
    Elimina una oferta asignatura nivel con ajax
    :param request:
    :return:
    """
    if OfertaAsignaturaNivel.objects.get(id=id).delete():
        return HttpResponse('Elemento eliminado')
    return HttpResponseServerError("error al eliminar")


@login_required
@require_http_methods(["POST"])
def oferta_asignatura_nivel_guardar(request):
    """
    Crea una oferta asignatura nivel con ajax
    :param request:
    :return:
    """
    oferta_asignatura_nivel = OfertaAsignaturaNivel()
    form = OfertaAsignaturaNivelForm(request.POST, instance=oferta_asignatura_nivel)
    if form.is_valid():
        if not (request.user.has_perm("academico.add_ofertaasignaturanivel", form.cleaned_data.get('oferta_pensum'))
                or request.user.has_perm("academico.add_ofertaasignaturanivel")):
            messages.warning(request, "No puede crear pensums en la carrera")
            raise PermissionDenied
        form.save()
        return JsonResponse(dict(id=oferta_asignatura_nivel.id))
    else:
        return HttpResponseServerError(form.errors)


@login_required
@permission_required_or_403('academico.view_ofertapensum', (OfertaPensum, 'id', 'id'), accept_global_perms=True, )
def oferta_pensum_detalle(request, id):
    """
        Desde la oferta academica se entra al detalle de un pensum ofertado.
    :param request:
    :param id:
    :return:
    """
    oferta_pensum = get_object_or_404(OfertaPensum, id=id)
    navegacion = ('Módulo académico',
                  [('Periódos académicos', reverse('academico:periodo_academico_lista')),
                   (oferta_pensum.oferta_academica.periodo_academico.nombre,
                    reverse('academico:periodo_academico_detalle',
                            kwargs={
                                'id': oferta_pensum.oferta_academica.periodo_academico.id})),
                   (oferta_pensum.oferta_academica.nombre, reverse('academico:oferta_academica_detalle',
                                                                   kwargs={
                                                                       'id': oferta_pensum.oferta_academica.id})),
                   ("Oferta de pensum", None)])
    asignaturas_ofertadas_ids = [oa.asignatura_nivel.id for oa in oferta_pensum.ofertas_asignatura_nivel.all()]
    return render(request, 'academico/oferta_pensum/detalle.html', locals())

@login_required
@permission_required('academico.delete_ofertapensum', raise_exception=True, )
@require_http_methods(["DELETE"])
def oferta_pensum_eliminar(request, id):
    """
    Elimina una oferta pensum con ajax
    :param request:
    :return:
    """
    if OfertaPensum.objects.get(id=id).delete():
        return HttpResponse('Elemento eliminado')
    return HttpResponseServerError("error al eliminar")


@login_required
@permission_required('academico.add_ofertapensum', raise_exception=True, )
@require_http_methods(["POST"])
def oferta_pensum_guardar(request):
    """
    Crea una oferta pensum con ajax
    :param request:
    :return:
    """
    oferta_pensum = OfertaPensum()

    form = OfertaPensumForm(request.POST, instance=oferta_pensum)
    if form.is_valid():
        form.save()
        return JsonResponse(dict(id=oferta_pensum.id))
    else:
        return HttpResponseServerError(form.errors)

@login_required
@permission_required('academico.view_periodoacademico', raise_exception=True, )
def periodo_academico_detalle(request, id):
    """
    Muestra el detalle de un periódo académico
    :param request:
    :param id:
    :return:
    """
    periodo_academico = get_object_or_404(PeriodoAcademico, id=id)

    periodos_lectivos = CatalogoItem.get_catalogos_items('PERIODO_ACADEMICO_PERIODO_LECTIVO')

    # CHOICE para oferta académica
    CHOICE_ESTADO = OfertaAcademica.CHOICE_ESTADO

    navegacion = ('Módulo académico',
                  [('Períodos académicos', reverse('academico:periodo_academico_lista')),
                   (periodo_academico.nombre, None)])

    return render(request, 'academico/periodo_academico/detalle.html', locals())


@login_required
@permission_required('academico.delete_periodoacademico', raise_exception=True, )
def periodo_academico_eliminar(request, id):
    """
    Elimina un registro de periodo academico
    :param request:
    :param id:
    :return:
    """
    periodo_academico = get_object_or_404(PeriodoAcademico, id=id)
    try:
        if periodo_academico.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('academico:periodo_academico_lista')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
        return redirect('academico:periodo_academico_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
    return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('academico.change_periodoacademico', raise_exception=True, )
@require_http_methods(["POST"])
def periodo_academico_guardar(request):
    """
    Crea o actualiza un período académico desde su modal-periodo-academico-editar
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        periodo_academico = PeriodoAcademico.objects.get(id=id)
    else:
        periodo_academico = PeriodoAcademico()

    form = PeriodoAcademicoForm(request.POST, instance=periodo_academico)
    if form.is_valid():
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)
    if request.POST.get('next'):
        return redirect(request.POST.get('next'))
    elif id:
        return redirect('academico:periodo_academico_detalle', id)
    return redirect(reverse('academico:index_curricular', ))


@login_required
@permission_required('academico.view_periodoacademico', raise_exception=True, )
def periodo_academico_lista(request):
    """
    Lista todos los periodos academicos
    :param request:
    :return:
    """
    navegacion = ('Módulo académico',
                  [('Períodos académicos', None)])
    periodos_academicos = PeriodoAcademico.objects.all()
    periodos_lectivos = CatalogoItem.get_catalogos_items('PERIODO_ACADEMICO_PERIODO_LECTIVO')
    return render(request, 'academico/periodo_academico/lista.html', locals())


@login_required
@permission_required('academico.delete_periodomatricula', raise_exception=True, )
def periodo_matricula_eliminar(request, id):
    """
    Elimina un registro de periodo matrícula
    :param request:
    :param id:
    :return:
    """
    periodo_matricula = get_object_or_404(PeriodoMatricula, id=id)
    try:
        if periodo_matricula.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
        return redirect('academico:oferta_academica_detalle', periodo_matricula.oferta_academica.id)

    except Exception as e:
        messages.warning(request, str(e))
    return HttpResponseServerError(render(request, '500.html'))


@require_http_methods(["POST"])
@permission_required('academico.change_periodomatricula', raise_exception=True, )
def periodo_matricula_guardar(request):
    """
    Crea o actualiza un período de matricula desde su modal-periodo-matricula-editar
    :param request:
    :return:
    """
    id = request.POST.get('id')
    if id:
        periodo_matricula = PeriodoMatricula.objects.get(id=id)
    else:
        periodo_matricula = PeriodoMatricula()

    form = PeriodoMariculaForm(request.POST, instance=periodo_matricula)
    if form.is_valid():
        form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, form.errors)

    return redirect('academico:oferta_academica_detalle', periodo_matricula.oferta_academica.id)


