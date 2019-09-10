from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseServerError
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from app.core.dto.datatable import DataTableParams
from app.core.utils.enums import MensajesEnum
from app.tesoreria.forms import CuentaCobrarForm, ComentarioForm, AbonoForm, TasaInteresForm, \
    InteresMensualForm
from app.tesoreria.models import CuentaCobrar, Comentario, Abono, TasaInteres, InteresMensual


# ////////////////////////Cuenta por cobrar//////////////
from app.tesoreria.utils.datatable import DatatableBuscar


@login_required
def index_tesoreria(request):
    """
    Index de la sección curricular del académico
    :param request:
    :return:
    """
    navegacion = ('Módulo académico',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria'))])
    return render(request, 'tesoreria/index_tesoreria.html', locals())


@login_required
@permission_required('tesoreria', raise_exception=True, )
def cuenta_cobrar_listar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied

    filtro = request.GET.get('filtro', '')
    page = request.GET.get('pagina')
    numero_items = request.GET.get('numero_items', '25')


    navegacion = ('Modulo financiero',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Cuentas por Cobrar', None)])
    # ver planificacion /pedi/resultado detalle
    cuenta_cobrar = CuentaCobrar.objects.all()

    if filtro:
        lista_de_cuentas = CuentaCobrar.buscar(filtro)
    else:
        lista_de_cuentas = CuentaCobrar.objects.all()

    paginator = Paginator(lista_de_cuentas, numero_items)
    try:
        cuenta_cobrar = paginator.page(page)
    except PageNotAnInteger:
        cuenta_cobrar = paginator.page(1)
    except EmptyPage:
        cuenta_cobrar = paginator.page(paginator.num_pages)
    return render(request, 'tesoreria/cuenta_cobrar/lista.html', locals())


@login_required
@permission_required('tesoreria', raise_exception=True, )
@require_http_methods(["POST"])
def cuenta_cobrar_lista_paginador(request):

    try:
        params = DataTableParams(request, **request.POST)
        DatatableBuscar.cuenta_cobrar(params)
        data = [{
            'id': it.id,
            'ci': it.cliente.numero_documento,
            'cliente': it.cliente.get_nombres_completos(),
            'monto': it.monto,
            'saldo': it.saldo,
            'estado': it.estado
        } for it in
            params.items]
        result = params.result(data)
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseServerError(e)


@login_required
def cuenta_cobrar_buscar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied

    filtro = request.GET.get('filtro')
    numero_items = request.GET.get('numero_items', '25')
    page = request.GET.get('pagina')

    if filtro:
        lista_cuenta_cobrar = CuentaCobrar.buscar(filtro)
    else:
        lista_cuenta_cobrar = CuentaCobrar.objects.all()
    paginator = Paginator(lista_cuenta_cobrar, numero_items)

    try:
        cuenta_cobrar = paginator.page(page)
    except PageNotAnInteger:
        cuenta_cobrar = paginator.page(1)
    except EmptyPage:
        cuenta_cobrar = paginator.page(paginator.num_pages)
    return render(request, 'tesoreria/cuenta_cobrar/lista.html', locals())


@login_required
@permission_required('tesoreria.change_cuentacobrar', raise_exception=True, )
@require_http_methods(['POST'])
def cuenta_cobrar_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        cuenta_cobrar = get_object_or_404(CuentaCobrar, id=id)
        if not (request.user.has_perm("tesoreria") or request.user.has_perm(
                "tesoreria", cuenta_cobrar)):
            raise PermissionDenied
    else:
        if not request.user.has_perm("tesoreria"):
            raise PermissionDenied
        cuenta_cobrar = CuentaCobrar()

    cuenta_cobrar_form = CuentaCobrarForm(request.POST, instance=cuenta_cobrar)
    if cuenta_cobrar_form.is_valid():
        cuenta_cobrar_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, cuenta_cobrar_form.errors)

    return redirect(next)


@login_required
@permission_required('tesoreria.delete_cuentacobrar', raise_exception=True, )
def cuenta_cobrar_eliminar(request, id):

    cuenta_cobrar = get_object_or_404(CuentaCobrar, id=id)
    try:
        if cuenta_cobrar.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('tesoreria:cuenta_cobrar_listar')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('tesoreria:cuenta_cobrar_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('tesoreria.view_cuentacobrar', raise_exception=True, )
def cuenta_cobrar_detalle(request, id):

    cuenta_cobrar = get_object_or_404(CuentaCobrar, id=id)

    navegacion = ('Modulo financiero',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Cuentas por Cobrar', reverse('tesoreria:cuenta_cobrar_listar')),
                   (cuenta_cobrar.cliente.get_nombres, None)])
    CHOICE_FORMAPAGO = Abono.FORMAPAGO
    return render(request, 'tesoreria/cuenta_cobrar/detalle.html', locals())


# ////////////////////////Titulo de Credito//////////////
"""@login_required
def titulo_credito_agregar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied
    form = TituloCreditoForm()
    if request.method == 'POST':
        form = TituloCreditoForm(request.POST)
        if form.is_valid():
            titulo_credito = form.save()
            return HttpResponseRedirect(reverse('tesoreria:cuenta_cobrar/detalle', args=(titulo_credito.id,)))
    return render(request, 'tesoreria/titulo_credito/agregar.html', locals())


@login_required
def titulo_credito_editar(request, id_titulo_credito):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied
    titulo_credito = get_object_or_404(TituloCredito, id=id_titulo_credito)
    form = TituloCreditoForm(instance=titulo_credito)
    if request.method == 'POST':
        form = TituloCreditoForm(request.POST, instance=titulo_credito)
        if form.is_valid():
            titulo_credito = form.save()
            return HttpResponseRedirect(reverse('tesoreria:cuenta_cobrar/detalle', args=(titulo_credito.id,)))
    return render(request, 'tesoreria/titulo_credito/agregar.html', locals())


@login_required
def titulo_credito_eliminar(request, id_titulo_credito):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied
    titulo_credito = get_object_or_404(CuentaCobrar, id=id_titulo_credito)
    titulo_credito.delete()
    return HttpResponseRedirect(reverse('tesoreria:cuenta_cobrar/detalle', args=(id_titulo_credito,)))

"""
# ////////////////////////Comentario//////////////

@login_required
@permission_required('tesoreria.change_comentario', raise_exception=True, )
@require_http_methods(['POST'])
def comentario_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        comentario = get_object_or_404(Comentario, id=id)
    else:
        comentario = Comentario()

    comentario_form = ComentarioForm(request.POST, instance=comentario)
    if comentario_form.is_valid():
        comentario_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, comentario_form.errors)

    return redirect(next)


@login_required
@permission_required('tesoreria.delete_comentario', raise_exception=True, )
def comentario_eliminar(request, id):

    comentario = get_object_or_404(Comentario, id=id)
    try:
        if comentario.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('tesoreria:cuenta_cobrar_detalle', comentario.cuenta_cobrar_id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('tesoreria:cuenta_cobrar_detalle', id)
    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


@login_required
@permission_required('tesoreria', raise_exception=True, )
def comentario_detalle(request, id):

    comentario = get_object_or_404(Comentario, id=id)

    navegacion = ('Módulo Académico',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Cuentas por Cobrar', reverse('tesoreria:cuenta_cobrar_listar')),
                   (comentario.concepto, None)])

    return render(request, 'tesoreria/comentario/detalle.html', locals())







"""@login_required
def comentario_listar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied

    lista_comentario = Comentario.objects.filter(activo=True)
    paginator = Paginator(lista_comentario, 25)
    page = request.GET.get('pagina')

    try:
        comentario = paginator.page(page)
    except PageNotAnInteger:
        comentario = paginator.page(1)
    except EmptyPage:
        comentario = paginator.page(paginator.num_pages)

    return render(request, 'tesoreria/cuenta_cobrar/detalle.html', locals())

"""""
# ////////////////////////Abono//////////////
@login_required
@permission_required('tesoreria.change_abono', raise_exception=True, )
@require_http_methods(['POST'])
def abono_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        abono = get_object_or_404(Abono, id=id)
    else:
        abono = Abono()

    abono_form = AbonoForm(request.POST, instance=abono)
    if abono_form.is_valid():
        abono_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, abono_form.errors)

    return redirect(next)


@login_required
@permission_required('tesoreria.delete_abono', raise_exception=True, )
def abono_eliminar(request, id):

    abono = get_object_or_404(Abono, id=id)

    try:
        if abono.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('tesoreria:cuenta_cobrar_detalle', abono.cuenta_cobrar_id)
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('tesoreria:cuenta_cobrar_detalle', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))


"""@login_required
def abono_listar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied

    lista_abono = Comentario.objects.filter(activo=True)
    paginator = Paginator(lista_abono, 25)
    page = request.GET.get('pagina')

    try:
        abono = paginator.page(page)
    except PageNotAnInteger:
        abono = paginator.page(1)
    except EmptyPage:
        abono = paginator.page(paginator.num_pages)

    return render(request, 'tesoreria/cuenta_cobrar/detalle.html', locals())
"""
# ////////////////////////Tasa interes//////////////
@login_required
@permission_required('tesoreria', raise_exception=True, )
def tasa_interes_listar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied

    navegacion = ('Modulo financiero',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Tasas de interes', None)])
    tasa_interes = TasaInteres.objects.all()
    return render(request, 'tesoreria/tasa_interes/lista.html', locals())


@login_required
@permission_required('tesoreria', raise_exception=True, )
@require_http_methods(["POST"])
def tasa_interes_lista_paginador(request):

    try:
        params = DataTableParams(request, **request.POST)
      #  DatatableBuscar.asignatura(params)
        data = params.items.values('id', 'Tasa','Fecha').all()
        result = params.result(list(data))
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseServerError(e)


@login_required
def tasa_interes_buscar(request):
    usuario = request.user
    if not usuario.is_member('tesoreria'):
        raise PermissionDenied

    filtro = request.GET.get('filtro')
    numero_items = request.GET.get('numero_items', '12')
    page = request.GET.get('pagina')

    if filtro:
        lista_tasa_interes= TasaInteres.buscar(filtro)
    else:
        lista_tasa_interes = TasaInteres.objects.all()
    paginator = Paginator(lista_tasa_interes, numero_items)

    try:
        tasa_interes = paginator.page(page)
    except PageNotAnInteger:
        tasa_interes = paginator.page(1)
    except EmptyPage:
        tasa_interes = paginator.page(paginator.num_pages)
    return render(request, 'tesoreria/tasa_interes/lista.html', locals())


@login_required
@permission_required('tesoreria.change_tasainteres', raise_exception=True, )
@require_http_methods(['POST'])
def tasa_interes_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        tasa_interes = get_object_or_404(TasaInteres, id=id)
    else:
        tasa_interes = TasaInteres()

    tasa_interes = TasaInteresForm(request.POST, instance=tasa_interes)
    if tasa_interes.is_valid():
        tasa_interes.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, tasa_interes.errors)

    return redirect(next)


@login_required
@permission_required('tesoreria.delete_tasainteres', raise_exception=True, )
def tasa_interes_eliminar(request, id):

    tasa_interes = get_object_or_404(TasaInteres, id=id)
    try:
        if tasa_interes.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('tesoreria:tasa_interes_listar')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('tesoreria:tasa_interes_listar', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))

# ////////////////////////Interes Mensual//////////////
@login_required
@require_http_methods(['POST'])
def interes_mensual_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        interes_mensual = get_object_or_404(InteresMensual, id=id)
        if not (request.user.has_perm("tesoreria") or request.user.has_perm(
                "tesoreria", TasaInteres)):
            raise PermissionDenied
    else:
        if not request.user.has_perm("tesoreria"):
            raise PermissionDenied
        interes_mensual = InteresMensual()

    interes_mensual = InteresMensualForm(request.POST, instance=interes_mensual)
    if interes_mensual.is_valid():
        interes_mensual.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, interes_mensual.errors)

    return redirect(next)


@login_required
@permission_required('tesoreria', raise_exception=True, )
def interes_mensual_eliminar(request, id):

    interes_mensual = get_object_or_404(InteresMensual, id=id)
    try:
        if interes_mensual.delete():
            messages.success(request, MensajesEnum.ACCION_ELIMINAR.value)
            return redirect('tesoreria:cuenta_cobrar_detalle')
        else:
            messages.warning(request, MensajesEnum.ACCION_ELIMINAR_ERROR.value)
            return redirect('tesoreria:cuenta_cobrar_detaller', id)

    except Exception as e:
        messages.warning(request, str(e))
        return HttpResponseServerError(render(request, '500.html'))