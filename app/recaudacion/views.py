from datetime import datetime, time

from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q

from api.tributacion.serializers import ComprobanteDetalleSerializer, ComprobanteDatosPrincipalesSerializer
from app.core.models import CatalogoItem
from app.recaudacion.models import OrdenPagoDetalle, Producto, OrdenPago
from app.tributacion.models import Comprobante, ComprobanteDetalle


def get_factura_individual_all(fecha, punto_emision_id, secuencial):
    """
    Genera todas las facturas individuales a emitir de acuerdo a las
    ordenes de pago (poseen pago) que no han sido facturadas
    :param fecha:
    :param punto_emision_id:
    :param secuencial:
    :return:
    """
    variable_secuencial = secuencial
    documentos_a_emitir = []
    documentos_a_generar = OrdenPago.objects.filter(
        Q(estado=OrdenPago.ESTADO_EMITIDA) &
        Q(punto_emision_uaa__punto_emision__id=punto_emision_id) &
        Q(pago__isnull=False) &
        Q(pago__fecha_pago__year=fecha.year) &
        Q(pago__fecha_pago__month=fecha.month) &
        Q(pago__fecha_pago__day=fecha.day) &
        (Q(comprobante__isnull=True) | (Q(comprobante__isnull=False) & Q(comprobante__estado=Comprobante.ESTADO_ANULADO)))
    ).exclude(comprobante__isnull=False, comprobante__estado=Comprobante.ESTADO_EMITIDA)

    for orden_pago in documentos_a_generar:
        # La orden de pago EMITIDA tienen items a facturar
        if orden_pago.ordenes_pago_detalle.filter(estado=OrdenPago.ESTADO_EMITIDA, producto__facturable=True).exists():
            comprobante = get_factura_individual(orden_pago, fecha, variable_secuencial)
            documentos_a_emitir.append(comprobante)
            variable_secuencial += 1

    return documentos_a_emitir, variable_secuencial


def get_factura_individual(orden_pago, fecha, variable_secuencial):
    """
    Genera la factura individual a emitir de acuerdo a una orden de pago (orden de pago EMITIDA)
    :param orden_pago:
    :param fecha:
    :param variable_secuencial:
    :return:
    """
    # Cuerpo del comprobante
    documento = get_init_factura(orden_pago, fecha, variable_secuencial)

    # Items del comprobante
    ordenes_pago_detalle = OrdenPagoDetalle.objects.filter(orden_pago=orden_pago,
                                                           estado=OrdenPago.ESTADO_EMITIDA,
                                                           producto__facturable=True
                                                           ).values('producto__id',
                                                                    'precio',
                                                                    'tipo_impuesto__id'
                                                                    ).annotate(cantidad=Sum('cantidad'),
                                                                               impuesto=Sum('impuesto'),
                                                                               total=Sum('total')
                                                                               ).order_by('producto__codigo').all()
    for detalle_unificado in ordenes_pago_detalle:
        # Obtengo los ids de las ordenes de pago detalle por producto para poder guardarlos en OrdenPagoDocumentoDetalle
        ords_pago_detalle = OrdenPagoDetalle.objects.filter(orden_pago=orden_pago,
                                                            estado=OrdenPago.ESTADO_EMITIDA,
                                                            producto__facturable=True,
                                                            producto_id=detalle_unificado['producto__id'],
                                                            precio=detalle_unificado['precio'],
                                                            tipo_impuesto_id=detalle_unificado['tipo_impuesto__id'])

        detalle_unificado['detalle_adicional'] = ''.join(ords_pago_detalle.filter(observacion__isnull=False).values_list('observacion', flat=True))
        detalle_unificado['ordenes_pago_detalle_ids'] = ords_pago_detalle.values_list('id', flat=True)
        documento_detalle = get_init_factura_detalle(detalle_unificado)
        documento['documento_detalles'].append(documento_detalle)

    # Totales e impuestos del comprobante
    documento_totales = get_factura_totales(documento)
    documento['documento_impuestos'] = get_factura_impuestos(documento)
    documento['subtotal_descuento'] = documento_totales['subtotal_descuento']
    documento['subtotal_sin_impuesto'] = documento_totales['subtotal_sin_impuesto']
    documento['total'] = documento_totales['total']

    return documento


def get_factura_impuestos(documento):
    """
    Genera los subtotales de toda la factura de acuerdo al tipo de impuesto
    :return:
    """
    documento_impuestos = []
    for documento_detalle in documento['documento_detalles']:
        documento_impuesto = get_init_factura_impuesto(documento_detalle['tipo_impuesto'])
        existe = get_factura_impuestos_buscar(documento_impuestos, documento_impuesto)
        if existe is not None:
            documento_impuestos[existe]['subtotal'] += float(documento_detalle['subtotal'])
            documento_impuestos[existe]['impuesto'] += float(documento_detalle['impuesto'])

        else:
            documento_impuesto['subtotal'] = float(documento_detalle['subtotal'])
            documento_impuesto['impuesto'] = float(documento_detalle['impuesto'])
            documento_impuestos.append(documento_impuesto)

    # Por seguridad para los decimales
    for impuesto in documento_impuestos:
        impuesto['subtotal'] = "{0:.4f}".format(round(impuesto['subtotal'], 4))
        impuesto['impuesto'] = "{0:.4f}".format(round(impuesto['impuesto'], 4))
    return documento_impuestos


def get_factura_totales(documento):
    """
    Calcula los totales del documento, total descuento, total sin impuesto y total
    :return:
    """
    subtotal_descuento = 0
    subtotal_sin_impuesto = 0
    total = 0
    for detalle in documento['documento_detalles']:
        subtotal_descuento += float(detalle['descuento'])
        subtotal_sin_impuesto += float(detalle['subtotal'])
        total += float(detalle['total'])

    return {'subtotal_descuento': "{0:.4f}".format(round(subtotal_descuento, 4)),
            'subtotal_sin_impuesto': "{0:.4f}".format(round(subtotal_sin_impuesto, 4)),
            'total': "{0:.2f}".format(round(total, 2))}


def get_factura_impuestos_buscar(lista, objeto):
    """
    Busca en la lista el objeto de IMPUESTO que
    recibe como paramtero
    :return:
    """
    for item in lista:
        if item['tipo_impuesto']['id'] == objeto['tipo_impuesto']['id']:
            return lista.index(item)
    return None


def get_init_factura(orden_pago, fecha_emision, variable_secuencial):
    """
    Crea un objeto Comprobante para la orden de pago
    :return:
    """
    hora_actual = time(datetime.now().hour, datetime.now().minute, datetime.now().second)

    documento = Comprobante()
    documento.numero_documento = orden_pago.punto_emision_uaa.punto_emision.new_codigo_factura(variable_secuencial)
    documento.persona = orden_pago.persona
    documento.direccion = orden_pago.direccion
    documento.tipo_documento = CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO_CONTABLE', 'FACTURA')
    documento.fecha_emision = datetime.combine(fecha_emision, hora_actual)
    documento.orden_pago = orden_pago

    documento_serializer = ComprobanteDatosPrincipalesSerializer(documento).data
    documento_serializer['documento_detalles'] = []
    return documento_serializer


def get_init_factura_detalle(op_detalle_unificado):
    """
    Crea un objeto Comprobante Detalle para la orden de pago detalle unificado
    :return:
    """
    producto = Producto.objects.get(id=op_detalle_unificado['producto__id'])

    documento_detalle = ComprobanteDetalle()
    documento_detalle.producto = producto
    documento_detalle.codigo = producto.codigo
    documento_detalle.detalle = producto.descripcion
    documento_detalle.detalle_adicional = op_detalle_unificado['detalle_adicional']
    documento_detalle.cantidad = op_detalle_unificado['cantidad']
    documento_detalle.precio = op_detalle_unificado['precio']
    documento_detalle.subtotal = op_detalle_unificado['cantidad'] * op_detalle_unificado['precio']
    documento_detalle.impuesto = op_detalle_unificado['impuesto']
    documento_detalle.tipo_impuesto = producto.tipo_impuesto
    documento_detalle.total = op_detalle_unificado['total']

    documento_detalle_serializer = ComprobanteDetalleSerializer(documento_detalle).data
    documento_detalle_serializer['orden_pago_detalle_ids'] = op_detalle_unificado['ordenes_pago_detalle_ids']
    return documento_detalle_serializer


def get_init_factura_impuesto(tipo_impuesto):
    """
    Crea un objeto Comprobante Impuesto de acuerdo al tipo de IMPUESTO que tiene
    la orden pago detalle unificado
    :return:
    """
    factura_impuesto = {}
    factura_impuesto['tipo_impuesto'] = tipo_impuesto
    factura_impuesto['impuesto'] = 0
    factura_impuesto['subtotal'] = 0

    return factura_impuesto