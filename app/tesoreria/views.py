from _decimal import Decimal
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseServerError
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods
from app.core.dto.datatable import DataTableParams
from app.core.models import Persona
from app.core.utils.enums import MensajesEnum
from app.tesoreria.forms import CuentaCobrarForm, ComentarioForm, AbonoForm, TasaInteresForm, \
    InteresMensualForm
from app.tesoreria.models import CuentaCobrar, Comentario, Abono, TasaInteres, InteresMensual
from app.reporte.utils import pdf as pdfUtil


# ////////////////////////Cuenta por cobrar//////////////
from app.tesoreria.utils.datatable import DatatableBuscar


@login_required
def index_tesoreria(request):
    """
    Index de la sección tesoreria
    :param request:
    :return:
    """
    navegacion = ('Módulo académico',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria'))])
    return render(request, 'tesoreria/index_tesoreria.html', locals())


# ////////////////////////Abono//////////////
@login_required
@permission_required('tesoreria.change_abono', raise_exception=True, )
@require_http_methods(['POST'])
def abono_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    id_cli = request.POST.get('cuenta_cobrar')
    cuenta_cobrar = CuentaCobrar.objects.get(id=str(id_cli))
    saldo = cuenta_cobrar.saldo
    interes = cuenta_cobrar.interes
    monto = Decimal(request.POST.get('monto'))
    aux_abo_int = 0.00
    if interes > 0:
        aux_abo_int = interes - monto

        if aux_abo_int < 0:
            aux = interes
            aux_abo_int = 0
        else:
            aux = monto

        request.POST._mutable = True
        request.POST['interes'] = Decimal(round(aux, 2))
        request.POST._mutable = False
    total = saldo - monto
    if id:
        abono = get_object_or_404(Abono, id=id)

    else:
        abono = Abono()

    abono_form = AbonoForm(request.POST, instance=abono)
    if abono_form.is_valid() and abono.monto <= cuenta_cobrar.saldo:
        CuentaCobrar.objects.values('saldo', 'interes').filter(id=id_cli).update(saldo=total, interes= aux_abo_int)

        abono_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, abono_form.errors)

    if abono.monto > cuenta_cobrar.saldo:
        messages.success(request, MensajesEnum.ABONO_MAYOR_SALDO.value)

    if total == 0:
        fecha_cancelacion = datetime.now()
        CuentaCobrar.objects.values('estado, fecha_cancelacion').filter(id=id_cli).update(estado=False, fecha_cancelacion=fecha_cancelacion)

    return redirect(next)

@login_required
@permission_required('tesoreria.delete_abono', raise_exception=True, )
def abono_eliminar(request, id):

    abono = get_object_or_404(Abono, id=id)
    cuenta_cobrar = CuentaCobrar.objects.get(id=str(abono.cuenta_cobrar_id))
    interes_cc = cuenta_cobrar.interes
    saldo = cuenta_cobrar.saldo
    monto = Decimal(abono.monto)
    total = saldo + monto
    interes = interes_cc + Decimal(abono.interes)

    CuentaCobrar.objects.values('saldo', 'interes').filter(id=abono.cuenta_cobrar_id).update(saldo=total, interes=interes)

    if total > 0:
        CuentaCobrar.objects.values('estado').filter(id=abono.cuenta_cobrar_id).update(saldo=False)

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


@login_required
@permission_required('tesoreria.view_abono', raise_exception=True, )
def abono_imprimir(request, id):

    abono = get_object_or_404(Abono, id=id)

    datos = dict(

        cliente=abono.cuenta_cobrar.cliente.get_nombres_completos(),
        fecha_pago=abono.fecha_pago,
        forma_pago=abono.forma_pago,
        referencia=abono.referencia,
        concepto=abono.concepto,
        monto=abono.monto,
        interes=abono.interes,
        saldo=abono.cuenta_cobrar.saldo,
        observacion=abono.observacion

    )


    return pdfUtil.generar_reporte('tesoreria_abono', datos, 'pdf', request)

# ////////////////////////Cliente//////////////

@login_required
@permission_required('tesoreria.change_cuentacobrar', raise_exception=True)
def cliente_lista(request):
    """
    Lista las clientes
    :param request:
    :return:
    """
    navegacion = ('Modulo financiero',
                  [('Tesorería', reverse('tesoreria:index_tesoreria')),
                   ('Clientes', None)])

    return render(request, 'tesoreria/cliente/lista.html', locals())


@login_required
@require_http_methods(["POST"])
@permission_required('tesoreria.change_cuentacobrar', raise_exception=True, )
def cliente_lista_paginador(request):
    """
    Lista los clientes con la paginación de datatable
    :param request:
    :return:
    """
    try:
        params = DataTableParams(request, **request.POST)
        DatatableBuscar.cliente(params)
        data = params.items.values('id', 'numero_documento', 'primer_apellido', 'segundo_apellido', 'primer_nombre',
                                   'segundo_nombre',
                                   'correo_electronico').all()
        result = params.result(list(data))
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseServerError(e)


@login_required
@permission_required('tesoreria.change_cuentacobrar', raise_exception=True)
def cliente_informacion_detallada(request, id):
    """
    Presenta la información de un determinado cliente
    :param request:
    :param id_funcionario: El identificador del funcionario
    :return: La página principal del funcionario
    """
    cliente = Persona.objects.get(id=id)

    navegacion = ('Módulo financiero',
                  [('Tesorería', reverse('tesoreria:index_tesoreria')),
                   ('Clientes', reverse('tesoreria:cliente_lista')),
                   (cliente.primer_nombre, None)])

    return render(request, 'tesoreria/cliente/informacion_detallada.html', locals())

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
@permission_required('tesoreria.view_comentario', raise_exception=True, )
def comentario_detalle(request, id):

    comentario = get_object_or_404(Comentario, id=id)
    cuenta_id=comentario.cuenta_cobrar.id

    navegacion = ('Módulo Académico',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Cuentas por Cobrar', reverse('tesoreria:cuenta_cobrar_listar')),
                   (comentario.cuenta_cobrar.cliente.get_nombres_completos, reverse('tesoreria:cuenta_cobrar_detalle',
                                                                                    args=[cuenta_id])),
                   (comentario.concepto, None)])

    return render(request, 'tesoreria/comentario/detalle.html', locals())


# ////////////////////////Cuenta por Cobrar//////////////

@login_required
@permission_required('tesoreria.view_cuentacobrar', raise_exception=True, )
def cuenta_cobrar_listar(request):

    filtro = request.GET.get('filtro', '')
    page = request.GET.get('pagina')
    numero_items = request.GET.get('numero_items', '25')


    navegacion = ('Modulo financiero',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Cuentas por Cobrar', None)])

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
@permission_required('tesoreria.view_cuentacobrar', raise_exception=True, )
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
@permission_required('tesoreria.view_cuentacobrar', raise_exception=True, )
def cuenta_cobrar_buscar(request):
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
    fecha_emision = request.POST.get('fecha_emision')
    date = parse_date(fecha_emision)
    saldo, interes = calcular_saldo(Decimal(request.POST.get('monto')), int(date.year), int(date.month))

    request.POST._mutable = True
    request.POST['saldo'] = Decimal(round(saldo, 2))
    request.POST['interes'] = Decimal(round(interes, 2))
    request.POST._mutable = False

    if id:
        cuenta_cobrar = get_object_or_404(CuentaCobrar, id=id)
    else:
        cuenta_cobrar = CuentaCobrar()

    cuenta_cobrar_form = CuentaCobrarForm(request.POST, instance=cuenta_cobrar)
    if cuenta_cobrar_form.is_valid():
        cuenta_cobrar_form.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, cuenta_cobrar_form.errors)

    return redirect(next)


def calcular_saldo(monto, anio, mes):
    fecha_actual = datetime.now()
    interes_total = 0.00
    tasa_interes = TasaInteres.objects.all()
    for tasa in tasa_interes:

        if int(tasa.anio) >= anio and int(tasa.mes) >= mes\
                and int(tasa.anio) <= int(fecha_actual.year) and int(tasa.mes) <= int(fecha_actual.month):

            interes = (monto * tasa.tasa)/100
            print(interes)
            interes_total = Decimal(interes_total) + Decimal(interes)

    saldo= monto + interes_total
    return saldo, interes_total

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
    cuenta_id=id

    navegacion = ('Modulo financiero',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Cuentas por Cobrar', reverse('tesoreria:cuenta_cobrar_listar')),
                   (cuenta_cobrar.cliente.get_nombres_completos, None)])
    CHOICE_FORMAPAGO = Abono.CHOICE_FORMAPAGO
    return render(request, 'tesoreria/cuenta_cobrar/detalle.html', locals())



# ////////////////////////Tasa interes//////////////
@login_required
@permission_required('tesoreria.view_tasainteres', raise_exception=True, )
def tasa_interes_listar(request):

    navegacion = ('Modulo financiero',
                  [('Tesoreria', reverse('tesoreria:index_tesoreria')),
                   ('Tasas de interes', None)])
    tasa_interes = TasaInteres.objects.all()
    return render(request, 'tesoreria/tasa_interes/lista.html', locals())


@login_required
@permission_required('tesoreria.view_tasainteres', raise_exception=True, )
@require_http_methods(["POST"])
def tasa_interes_lista_paginador(request):

    try:
        params = DataTableParams(request, **request.POST)
      #  DatatableBuscar.asignatura(params)
        data = params.items.values('id', 'Tasa','Fecha').all()
        data = [{
            'id': it.id,
            'tasa': it.tasa,
            'fecha': it.fecha
        } for it in
            params.items]
        result = params.result(data)
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseServerError(e)



@login_required
@permission_required('tesoreria.change_tasainteres', raise_exception=True, )
@require_http_methods(['POST'])
def tasa_interes_guardar(request):
    next = request.POST.get('next')
    tasa_interes = TasaInteres()
    tasa_interes = TasaInteresForm(request.POST, instance=tasa_interes)
    if tasa_interes.is_valid() and validar_tasa_interes(request.POST.get('anio'), request.POST.get('mes')):
        tasa_interes.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)
    else:
        messages.warning(request, MensajesEnum.ACCION_NUEVO_TASA.value)

    return redirect(next)


def validar_tasa_interes(anio, mes):
    val = True
    tasa_interes = TasaInteres.objects.all()
    for tasa in tasa_interes:
        print(tasa.anio, tasa.mes)
        if str(tasa.anio) == str(anio) and str(tasa.mes) == str(mes):
            val = False

    return val

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
@permission_required('tesoreria.change_interesmensual', raise_exception=True, )
@require_http_methods(['POST'])
def interes_mensual_guardar(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        interes_mensual = get_object_or_404(InteresMensual, id=id)

    else:

        interes_mensual = InteresMensual()

    interes_mensual = InteresMensualForm(request.POST, instance=interes_mensual)
    if interes_mensual.is_valid():
        interes_mensual.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, interes_mensual.errors)

    return redirect(next)


@login_required
def interes_mensual_guardar_static(id_cli, tasa, fecha):
    """
    :param request:
    :return:
    """
    valor = 0

    tasa_interes_mensual = InteresMensual()

    tasa_interes_mensual.cuenta_cobrar = id_cli
    tasa_interes_mensual.tasa = tasa
    tasa_interes_mensual.fecha = fecha
    tasa_interes_mensual.valor = valor


    try:
        tasa_interes_mensual.save()
        message = MensajesEnum.ACCION_GUARDAR.value,

    except NameError:
        message = 'Solicitud incorrecta'

    return JsonResponse({'mensaje': message})

def interes_mensual_guardar_static(request):
    next = request.POST.get('next')
    id = request.POST.get('id')
    if id:
        interes_mensual = get_object_or_404(InteresMensual, id=id)

    else:

        interes_mensual = InteresMensual()

    interes_mensual = InteresMensualForm(request.POST, instance=interes_mensual)
    if interes_mensual.is_valid():
        interes_mensual.save()
        messages.success(request, MensajesEnum.ACCION_GUARDAR.value)

    else:
        messages.warning(request, interes_mensual.errors)

    return redirect(next)

@login_required
@permission_required('tesoreria.delete_interesmensual', raise_exception=True, )
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


