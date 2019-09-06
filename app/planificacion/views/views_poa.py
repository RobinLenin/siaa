from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse

from app.planificacion.forms import *


@login_required
@permission_required('planificacion.change_actividad', raise_exception=True)
def actividad_detalle(request, id):
    """
    Ver detalle de actividad
    :param request:
    :param id: id actividad
    :return: html detalle
    """
    actividad = get_object_or_404(Actividad, id=id)
    presupuesto = actividad.presupuesto if hasattr(actividad, 'presupuesto') else Presupuesto(actividad=actividad)
    presupuesto_form = PresupuestoForm(instance=presupuesto)
    return render(request, 'planificacion/actividad/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_actividad', raise_exception=True)
def actividad_eliminar(request, **kwargs):
    """
    Eliminar actividad por GET  o DELETE(ajax)
    :param request:
    :param kwargs: {'id': id_actividad}
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            actividad = Actividad.objects.get(**kwargs)
            meta_anual = actividad.meta_anual.id
            if actividad.delete():
                meta_anual.distribuir_porcentaje()
                if not request.is_ajax():
                    messages.success(request, 'Elemento eliminado')
                return redirect('planificacion:meta_anual_detalle', meta_anual.id)
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró la actividad a eliminar')
        except Exception:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar la actividad')
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    if kwargs.get('id'):
        return redirect('planificacion:activiadad_detalle', kwargs.get('id'))
    return redirect('planificacion:plan_operativo_lista')


@login_required
@permission_required('planificacion.add_actividad', raise_exception=True, )
def actividad_guardar(request):
    """
    Guardar/crear Actividad
    :param request: datos del modal
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            actividad = Actividad.objects.get(id=id)
        else:
            actividad = Actividad()
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            actividad = form.save()
            actividad.meta_anual.distribuir_porcentaje()
            messages.success(request, 'Actividad %s con exito' % ('modificada' if id else 'creada'))
        else:
            messages.error(request, form.errors)
        if request.POST.get('next'):
            return HttpResponseRedirect(request.POST.get('next'))
        elif id:
            return redirect('planificacion:actividad_detalle', id)
        elif form.cleaned_data.get('meta_anual'):
            return redirect('planificacion:meta_anual_detalle',
                            form.cleaned_data.get('meta_anual').id)
    return HttpResponseRedirect(reverse('planificacion:plan_operativo_lista', ))


# POA
@login_required
@permission_required('planificacion.view_planoperativo', raise_exception=True, )
def plan_operativo_detalle(request, id):
    """
    Mostrar detalle de plan operativo
    :param request:
    :param id: id de plan
    :return: html detalle
    """
    plan_operativo = get_object_or_404(PlanOperativo, id=id)
    if request.user.is_superuser:
        metas_anuales = MetaAnual.objects.filter(
            indicador__resultado__objetivo_operativo__objetivo_estrategico__plan_estrategico=plan_operativo.plan_estrategico,
            periodo=plan_operativo.periodo).all()
    else:
        metas_anuales = MetaAnual.objects.filter(
            indicador__resultado__objetivo_operativo__objetivo_estrategico__plan_estrategico=plan_operativo.plan_estrategico,
            periodo=plan_operativo.periodo,
            indicador__resultado__responsables__uaapuesto__asignacionpuesto__funcionario=request.user.funcionario).all()
    return render(request, 'planificacion/plan_operativo/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_planoperativo', raise_exception=True, )
def plan_operativo_eliminar(request, **kwargs):
    """
    Eliminar plan oprativo por GET  o DELETE (ajax)
    :param request:
    :param kwargs: {'id': id_plan}
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            plan = PlanOperativo.objects.get(**kwargs)
            plan_estrategico_id = plan.plan_estrategico.id
            if plan.delete():
                if not request.is_ajax():
                    messages.success(request, 'Plan Operativo eliminado')
                return redirect('planificacion:plan_estrategico_detalle', plan_estrategico_id)
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el plan a eliminar')
        except Exception:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar el plan operativo')
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    if kwargs.get('id'):
        return redirect('planificacion:plan_operativo_detalle', kwargs.get('id'))
    return redirect('planificacion:plan_operativo_lista')


@login_required
@permission_required('planificacion.add_planoperativo', raise_exception=True, )
def plan_operativo_guardar(request):
    """
    Guardar/Crear plan operativo
    :param request: datos modal
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            plan_operativo = PlanOperativo.objects.get(id=id)
        else:
            plan_operativo = PlanOperativo()
        form = PlanOperativoForm(request.POST, instance=plan_operativo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan Operativo %s con exito' % ('modificado' if id else 'creado'))
        else:
            messages.error(request, form.errors)
        redirect('planificacion:plan_estrategico_detalle', request.POST.get('plan_estrategico'))
    return HttpResponseRedirect(reverse('planificacion:plan_estrategico_lista', ))


@login_required
# @permission_required('planificacion.view_planoperativo', raise_exception=True, )
def plan_operativo_lista(request):
    """
    Función vista para la página inicio de planes operativos,
    :param request:
    :return: html lista
    """
    if request.user.is_superuser:
        planes_operativos = PlanOperativo.objects.all()
    else:
        funcionario = request.user.funcionario
        planes_operativos = PlanOperativo.objects.filter(
            periodo__metas_anuales__indicador__resultado__responsables__uaapuesto__asignacionpuesto__funcionario=funcionario).distinct().all()
    return render(request, 'planificacion/plan_operativo/lista.html', locals())


@login_required
@permission_required('planificacion.delete_presupuesto', raise_exception=True, )
def presupuesto_eliminar(request, **kwargs):
    """
    Eliminar presupuesto
    :param request:
    :param kwargs: {'id': id_presupuesto}
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            presupuesto = Presupuesto.objects.get(**kwargs)
            actividad_id = presupuesto.actividad.id
            if presupuesto.delete():
                if not request.is_ajax():
                    messages.success(request, 'Elemento eliminado')
                return redirect('planificacion:actividad_detalle', actividad_id)
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el presupuesto a eliminar')
        except Exception:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar la presupuesto')
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return redirect('planificacion:plan_operativo_lista')


@login_required
@permission_required('planificacion.add_presupuesto', raise_exception=True, )
def presupuesto_guardar(request):
    """
    Guardar/crear presupuesto
    :param request: datos del modal
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            presupuesto = Presupuesto.objects.get(id=id)
        else:
            presupuesto = Presupuesto()
        form = PresupuestoForm(request.POST, instance=presupuesto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Presupuesto %s con exito' % ('modificado' if id else 'creado'))
            redirect('planificacion:actividad_detalle', presupuesto.actividad.id)
        if request.POST.get('next'):
            return HttpResponseRedirect(request.POST.get('next'))
        elif form.cleaned_data.get('actividad'):
            return render(request, 'planificacion/actividad/detalle.html',
                          {'presupuesto_form': form, 'actividad': form.cleaned_data.get('actividad')})

    return HttpResponseRedirect(reverse('planificacion:plan_operativo_lista', ))


@login_required
@permission_required('planificacion.change_verificacion', raise_exception=True, )
def verificacion_detalle(request, id):
    """
    Ver detalle de Verificacion
    :param request:
    :param id: id de verificacion
    :return: html detalle
    """
    verificacion = get_object_or_404(Verificacion, id=id)
    return render(request, 'planificacion/verificacion/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_verificacion', raise_exception=True, )
def verificacion_eliminar(request, **kwargs):
    """
    Eliminar Verificacion GET  O DELETE(ajax)
    :param request:
    :param kwargs: {'id': id_verificacion}
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            verificacion = Verificacion.objects.get(**kwargs)
            actividad_id = verificacion.actividad.id
            if verificacion.delete():
                if not request.is_ajax():
                    messages.success(request, 'Elemento eliminado')
                return redirect('planificacion:actividad_detalle', actividad_id)
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró la verificacion a eliminar')
        except Exception as e:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar la verificacion')
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    elif kwargs.get('id'):
        return redirect('planificacion:verificacion_detalle', kwargs.get('id'))
    return redirect('planificacion:plan_operativo_lista')


@login_required
@permission_required('planificacion.add_verificacion', raise_exception=True, )
def verificacion_guardar(request):
    """
    Crear/Guardar Verificacion
    :param request: datos del mdal
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            verificacion = Verificacion.objects.get(id=id)
        else:
            verificacion = Verificacion()
        form = VerificacionForm(request.POST, request.FILES, instance=verificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medio de verificacion %s con exito' % ('modificado' if id else 'creado'))
        else:
            messages.error(request, form.errors)
        if request.POST.get('next'):
            return HttpResponseRedirect(request.POST.get('next'))
        elif id:
            return redirect('planificacion:verificacion_detalle', id)
        elif form.cleaned_data.get('actividad'):
            return redirect('planificacion:actividad_detalle',
                            form.cleaned_data.get('actividad').id)
    return HttpResponseRedirect(reverse('planificacion:plan_operativo_lista', ))
