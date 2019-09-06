from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, \
    HttpResponseNotModified
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from app.core.models import PeriodoFiscal
from app.planificacion.forms import *
from app.planificacion.models import Estrategia
from app.planificacion.models import Politica
from app.reporte.utils.pdf import html_a_pdf
from app.talento_humano.models import Puesto


@login_required
@permission_required('planificacion.delete_estrategia', raise_exception=True)
def estrategia_eliminar(request, **kwargs):
    """
    Metodo para eliminar una estrategia (ahora solo por ajax)
    :param request:
    :param kwargs: {'id': id_estrategia}
    :return:
    """
    if request.method == 'DELETE':
        if Estrategia.objects.get(**kwargs).delete():
            return HttpResponse('Elemento eliminado')
    return HttpResponseNotModified('Error al eliminar')


@login_required
@permission_required('planificacion.add_estrategia', raise_exception=True, )
def estrategia_guardar(request):
    """
    Metodo para agregar una estrategia
    :param request: {datos json}
    :return:
    """
    # politica solo viene por ajax
    if request.method == 'POST' and request.is_ajax():
        data = request.POST.dict()
        id = data.pop('id', False)
        if id:
            estrategia, nuevo = Estrategia.objects.update_or_create(id=id, defaults=data)
        else:
            estrategia = Estrategia.objects.create(**data)
        return JsonResponse({'item_id': estrategia.id})
    return HttpResponseBadRequest('Metodo no valido')


@login_required
def index(request):
    """
    Index de planificacion, solo muestra acceso al listado de pedis y poas
    :param request: 
    :return: 
    """
    return render(request, 'planificacion/index.html', locals())


@login_required
@permission_required('planificacion.change_indicador', raise_exception=True)
def indicador_detalle(request, id):
    """
    Ver detalle del indicador
    :param request:
    :param id: id del indicador
    :return:
    """
    indicador = get_object_or_404(Indicador, id=id)
    periodos_fiscales = PeriodoFiscal.objects.filter(
        id__in=indicador.resultado.objetivo_operativo.objetivo_estrategico.plan_estrategico.periodos.values_list('id',
                                                                                                                 flat=True)).exclude(
        metas_anuales__indicador=indicador).all()
    return render(request, 'planificacion/indicador/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_indicador', raise_exception=True)
def indicador_eliminar(request, **kwargs):
    """
        Metodo para eliminar una indicador por GET
        :param request:
        :param kwargs: {'id':resultado_id}
        :return:
        """
    if request.method == 'GET' or request.method == 'DELETE':
        try:
            indicador = Indicador.objects.get(**kwargs)
            resultado_id = indicador.resultado.id
            if indicador.delete():
                if request.is_ajax():
                    return HttpResponse()
                messages.success(request, 'Elemento eliminado')
                return redirect('planificacion:resultado_detalle', resultado_id)
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el indicador a eliminar')
        except Exception as e:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar el indicador ' + str(e))
    if not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@permission_required('planificacion.add indicador', raise_exception=True)
def indicador_guardar(request):
    """
    guardar o crear Indicador
    :param request:  datos del modal POST
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            indicador = Indicador.objects.get(id=id)
        else:
            indicador = Indicador()
        form = IndicadorForm(request.POST, instance=indicador)
        if form.is_valid():  # and ingredienteFormset.is_valid() and instruccionFormset.is_valid():
            indicador = form.save()
            return redirect('planificacion:indicador_detalle', indicador.id)
        else:
            messages.error(request, form.errors)
            if id:
                return redirect('planificacion:indicador_detalle', indicador.id)
            else:
                return redirect('planificacion:resultado_detalle', request.POST.get('resultado'))
    messages.error(request, 'Petición inválida!!')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@permission_required('planificacion.change_metaanual', raise_exception=True)
def meta_anual_detalle(request, id):
    """
    Ver detalle de la Meta anual
    :param request:
    :param id: id de la meta
    :return: html detalle
    """
    meta_anual = get_object_or_404(MetaAnual, id=id)
    periodos_fiscales = PeriodoFiscal.objects.filter(
        id__in=meta_anual.indicador.resultado.objetivo_operativo.objetivo_estrategico.plan_estrategico.periodos.values_list(
            'id', flat=True))
    # mismo resutado verificar mejor
    # PeriodoFiscal.objects.filter(
    #    planes_estrategicos__objetivos_estrategicos__objetivos_operativos__resultados__indicadores__metas_anuales__id=meta_anual.id)
    return render(request, 'planificacion/meta_anual/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_metaanual', raise_exception=True)
def meta_anual_eliminar(request, **kwargs):
    """
        Metodo para eliminar una meta_anual   por ajax
        :param request:
        :param kwargs: {'id':meta_id}
        :return:
        """
    if request.method == 'DELETE':
        try:
            meta_anual = MetaAnual.objects.get(**kwargs)
            if meta_anual.delete():
                return HttpResponse()
        except Exception as e:
            print(e)
    return HttpResponseBadRequest()


@login_required
@permission_required('planificacion.change_metaanual', raise_exception=True)
def meta_anual_guardar(request):
    """
    Guardar / crear Meta anual
    :param request: datos del modal
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            meta_anual = MetaAnual.objects.get(id=id)
        else:
            meta_anual = MetaAnual()
        form = MetaAnualForm(request.POST, instance=meta_anual)
        if form.is_valid():
            meta_anual = form.save()
        else:
            messages.error(request, form.errors)
    else:
        messages.error(request, 'Petición inválida!!')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@permission_required('planificacion.change_objetivoestrategico', raise_exception=True)
def objetivo_estrategico_detalle(request, id):
    """
    Metodo para ver el objetivo estrategico detalle
    :param request: id del objetivo
    :return: html detalle
    """
    objetivo_estrategico = ObjetivoEstrategico.objects.filter(id=id).first()
    EJES_ESTRATEGICOS = ObjetivoEstrategico.EJES_ESTRATEGICOS
    return render(request, 'planificacion/objetivo_estrategico/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_objetivoestrategico', raise_exception=True)
def objetivo_estrategico_eliminar(request, **kwargs):
    """
    Metodo para eliminar objetivo estrategico
    :param request:
     :param kwargs: {'id': id_objetivo}
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            objetivo = ObjetivoEstrategico.objects.get(**kwargs)
            plan_estrategico_id = objetivo.plan_estrategico.id
            if objetivo.delete():
                if not request.is_ajax():
                    messages.success(request, 'Objetivo Estrategico eliminado')
                return redirect('planificacion:plan_estrategico_detalle', plan_estrategico_id)
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el objetivo a eliminar')
        except Exception:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar el objetivo estrategico')
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    if kwargs.get('id'):
        return redirect('planificacion:objetivo_estrategico_detalle', kwargs.get('id'))
    return redirect('planificacion:plan_estrategico_lista')


@login_required
@permission_required('planificacion.add_objetivoestrategico', raise_exception=True)
def objetivo_estrategico_guardar(request):
    """
    Metodo para agregar/guardar un  objetivo estrategico
    :param request: datos del modal
    :return: html
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            objetivo_estrategico = ObjetivoEstrategico.objects.get(id=id)
        else:
            objetivo_estrategico = ObjetivoEstrategico()
        form = ObjetivoEstrategicoForm(request.POST, instance=objetivo_estrategico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Objetivo Estrategico %s con exito' % ('modificado' if id else 'creado'))
            if id:
                return redirect('planificacion:objetivo_estrategico_detalle', id)
            elif form.cleaned_data.get('plan_estrategico'):
                return redirect('planificacion:plan_estrategico_detalle',
                                form.cleaned_data.get('plan_estrategico').id)
        else:
            messages.error(request, form.errors)
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:plan_estrategico_lista', ))


@login_required
@permission_required('planificacion.change_objetivooperativo', raise_exception=True)
def objetivo_operativo_detalle(request, id=None):
    """
    Ver objetivo operativo mediante su template
    :param request: id del objetivo
    :return:
    """
    objetivo_operativo = get_object_or_404(ObjetivoOperativo, id=id)
    # puestos =  Puesto.objects.all(), ahora solo obtengo values para que no demore la carga
    puestos_values = Puesto.objects.values('id', 'denominacion', 'grupo_ocupacional__regimen_laboral__nombre')
    return render(request, 'planificacion/objetivo_operativo/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_objetivooperativo', raise_exception=True)
def objetivo_operativo_eliminar(request, **kwargs):
    """
    Metodo para eliminar un nuevo objetivo operativo (ajax o GET)
    :param request:
     :param kwargs: {'id': id_objetivo}
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            objetivo = ObjetivoOperativo.objects.get(**kwargs)
            objetivo_estrategico_id = objetivo.objetivo_estrategico.id
            if objetivo.delete():
                if not request.is_ajax():
                    messages.success(request, 'Objetivo Opearativo eliminado')
                return HttpResponseRedirect(
                    reverse('planificacion:objetivo_estrategico_detalle', kwargs={'id': objetivo_estrategico_id}))
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el objetivo a eliminar')
        except Exception:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar el objetivo operativo')
    if not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:objetivo_operativo_detalle', kwargs=kwargs))


@login_required
@permission_required('planificacion.add_objetivooperativo', raise_exception=True)
def objetivo_operativo_guardar(request):
    """
    Guardar datos recibidos delmodal
    :param request: {json datos del modal por POST}
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if request.POST.get('id'):
            objetivo_operativo = ObjetivoOperativo.objects.get(id=request.POST.get('id'))
        else:
            objetivo_operativo = ObjetivoOperativo()
        form = ObjetivoOperativoForm(request.POST, instance=objetivo_operativo)
        if form.is_valid():
            objetivo_operativo = form.save()
            if request.is_ajax():
                return JsonResponse({'item_id': objetivo_operativo.id})
            messages.success(request, 'Objetivo %s correctamente' % 'editado' if id else 'modificado')
        else:
            messages.error(request, form.errors)
        if id:
            return redirect('planificacion:objetivo_operativo_detalle', id)
        elif form.cleaned_data.get('objetivo_estrategico'):
            return redirect('planificacion:objetivo_estrategico_detalle',
                            form.cleaned_data.get('objetivo_estrategico').id)
    if not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:plan_estrategico_lista'))


@login_required
@permission_required('planificacion.change_planestrategico', raise_exception=True)
def plan_estrategico_detalle(request, id):
    """
    Detalle del plan estrategico institucional
    :param request: 
    :param id: 
    :return: html detalle
    """
    plan_estrategico = PlanEstrategico.objects.filter(id=id).first()
    periodos_fiscales = PeriodoFiscal.objects.all().order_by('-nombre')
    EJES_ESTRATEGICOS = ObjetivoEstrategico.EJES_ESTRATEGICOS
    return render(request, 'planificacion/plan_estrategico/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_planestrategico', raise_exception=True)
def plan_estrategico_eliminar(request, **kwargs):
    """
    Metodo para eliminar un  plan estrategico desde su vista de edicion, o el listado de planes(ajax)
    :param request: id
    :return:
    """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            plan = PlanEstrategico.objects.get(**kwargs)
            if plan.delete():
                if not request.is_ajax():
                    messages.success(request, 'Elemento eliminado')
                else:
                    return JsonResponse('Elemento eliminado')
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el plan a eliminar')
        except Exception:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar el plan estrategico')
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:plan_estrategico_lista'))


@login_required
@permission_required('planificacion.add_planestrategico', raise_exception=True)
def plan_estrategico_guardar(request):
    """
        Metodo para
     - agregar un nuevo plan estrategico desde el listado de planes
    -  editar un plan desde el detalle de plan
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            plan_estrategico = PlanEstrategico.objects.get(id=id)
        else:
            plan_estrategico = PlanEstrategico()
        form = PlanEstrategicoForm(request.POST, instance=plan_estrategico)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return JsonResponse({'plan_estrategico_id': plan_estrategico.id, 'activo': plan_estrategico.activo})
            messages.success(request, 'Plan Estrategico %s con exito' % ('modificado' if id else 'creado'))
        else:
            messages.error(request, form.errors)
        if id:
            return redirect('planificacion:plan_estrategico_detalle', id)
    elif not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:plan_estrategico_lista', ))


@login_required
def plan_estrategico_lista(request):
    """
    Muestra la lista de planes estrategicos, con agregar, eliminar
    :param request: 
    :return: 
    """
    planes_estrategicos = PlanEstrategico.objects.all().order_by('-activo', '-id')
    periodos_fiscales = PeriodoFiscal.objects.all().order_by('-nombre')
    return render(request, 'planificacion/plan_estrategico/lista.html', locals())


@login_required
def plan_estrategico_reporte_detalle(request, id):
    """
    Metodo para obtener el reporte general del PEDI
    :param request: id
    :return:
    """
    plan_estrategico = PlanEstrategico.objects.filter(id=id).first()
    context = {'plan_estrategico': plan_estrategico,
               'size': 'A4 landscape',
               'title': 'Plan Estrategico',
               'titulo': 'Universidad Nacional de Loja',
               'subtitulo': 'Sistema de Planificacion',
               'asunto': 'Plan Estrategico Institucional',
               'detalle': 'Documentos generados a partir de las',
               'fecha': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
               'usuario': request.user
               }
    template = 'planificacion/plan_estrategico/reporte_detalle.html'
    return html_a_pdf(request, template, context, filename="Plan Estrategico %s" % plan_estrategico.nombre)


@login_required
@permission_required('planificacion.delete_politica', raise_exception=True)
def politica_eliminar(request, **kwargs):
    """
    Metodo para eliminar politica (ajax)
    :param request:
     :param kwargs: {'id': id_politica}
    :return:
    """
    if request.method == 'DELETE':
        if Politica.objects.get(**kwargs).delete():
            return HttpResponse('Elemento eliminado')
    return HttpResponseNotModified('Error al eliminar')


@login_required
@permission_required('planificacion.add_politica', raise_exception=True)
def politica_guardar(request):
    """
    Metodo para guardar una politica (ajax)
    :param request: {datos en json}
    :return:
    """
    # politica solo viene por ajax
    if request.method == 'POST' and request.is_ajax():
        data = request.POST.dict()
        id = data.pop('id', False)
        if id:
            politica, nuevo = Politica.objects.update_or_create(id=id, defaults=data)
        else:
            politica = Politica.objects.create(**data)
        return JsonResponse({'item_id': politica.id})
    return HttpResponseBadRequest('Metodo no valido')


@login_required
@permission_required('planificacion.change_resultado', raise_exception=True)
def resultado_detalle(request, id):
    """
    Ver detalle del resultado
    :param request:
    :param id: id del resultado
    :return:
    """
    resultado = get_object_or_404(Resultado, id=id)
    puestos_values = Puesto.objects.values('id', 'denominacion', 'grupo_ocupacional__regimen_laboral__nombre')
    return render(request, 'planificacion/resultado/detalle.html', locals())


@login_required
@permission_required('planificacion.delete_resultado', raise_exception=True)
def resultado_eliminar(request, **kwargs):
    """
        Metodo para eliminar una resultado por ajax(DELETE) o GET
        :param request:
        :param kwargs: {'id':resultado_id}
        :return:
        """
    if request.method == 'DELETE' or request.method == 'GET':
        try:
            resultado = Resultado.objects.get(**kwargs)
            objetivo_operativo_id = resultado.objetivo_operativo.id
            if resultado.delete():
                if not request.is_ajax():
                    messages.success(request, 'Elemento eliminado')
                return HttpResponseRedirect(
                    reverse('planificacion:objetivo_operativo_detalle', kwargs={'id': objetivo_operativo_id}))
        except ObjectDoesNotExist:
            if not request.is_ajax():
                messages.error(request, 'No se encontró el resultado a eliminar')
        except Exception as e:
            if not request.is_ajax():
                messages.error(request, 'Error al eliminar el resultado' + str(e), )
    if not request.is_ajax():
        messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:resultado_detalle', kwargs=kwargs))


@login_required
@permission_required('planificacion.add_resultado', raise_exception=True)
def resultado_guardar(request):
    """
    Editar/crear Resultado mediante su modal
    :param request: datos del modal
    :return:
    """
    if request.method == 'POST':
        id = request.POST.get('id')
        if request.POST.get('id'):
            resultado = Resultado.objects.get(id=request.POST.get('id'))
        else:
            resultado = Resultado()
        form = ResultadoForm(request.POST, instance=resultado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resultado %s correctamente' % ('editado' if id else 'modificado'))
        else:
            messages.error(request, form.errors)
        if request.POST.get('next'):
            return HttpResponseRedirect(request.POST.get('next'))
        elif id:
            return redirect('planificacion:resultado_detalle', id)
        elif form.cleaned_data.get('objetivo_operativo'):
            return redirect('planificacion:objetivo_operativo_detalle',
                            form.cleaned_data.get('objetivo_operativo').id)
    messages.error(request, 'Petición inválida!!')
    return HttpResponseRedirect(reverse('planificacion:plan_estrategico_lista'))
