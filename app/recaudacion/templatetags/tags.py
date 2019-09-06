from datetime import datetime

from django import template

from app.recaudacion.models import OrdenPago, Pago
from app.tributacion.models import Comprobante

register = template.Library()

def get_total_documentos(documentos):
    impuesto =0
    subtotal = 0
    total=0
    total_emitidas = 0
    total_anuladas = 0
    for documento in documentos:
        for detalle in documento['documento_detalles']:
            impuesto += float(detalle['impuesto'])
            subtotal += float(detalle['subtotal'])
            total += float(detalle['total'])
        #Total de emitidas y anuladas
        if documento ['estado'] == Comprobante.ESTADO_EMITIDA:
            total_emitidas += float(documento['total'])
        elif documento ['estado'] == Comprobante.ESTADO_ANULADO:
            total_anuladas += float(documento['total'])

    return {'total': format(round(total,2), '.2f'),
            'subtotal': format(round(subtotal,2), '.2f'),
            'impuesto': format(round(impuesto,2), '.2f'),
            'total_emitidas': format(round(total_emitidas, 2), '.2f'),
            'total_anuladas': format(round(total_anuladas, 2), '.2f')
            }

def get_punto_emision_total(totales, punto_emision_uaa):
    total_emitidas = 0
    total_anuladas = 0
    total_formas_pago = {}

    for key, value in Pago.CHOICE_FORMA_PAGO:
        total_formas_pago[key] = 0

    # Total emitidas por forma de pago
    for detalle in punto_emision_uaa['ordenes_pago_emitidas']:
        # Tiene un pago asociado
        orden_pago = OrdenPago.objects.get(id=detalle['orden_pago'])
        if orden_pago.pago:
            total_formas_pago [orden_pago.pago.forma_pago] += float(detalle['total'])
        # No tiene un pago asociado (ordenes de pago anteriores)
        else:
            if detalle['transferencia']:
                total_formas_pago [Pago.FORMA_PAGO_TRANSFERENCIA] += float(detalle['total'])
            else:
                total_formas_pago [Pago.FORMA_PAGO_EFECTIVO] += float(detalle['total'])

    # Total emitidas
    for item in total_formas_pago:
        total_emitidas += total_formas_pago[item]

    # Total anuladas
    for orden_pago_detalle in punto_emision_uaa['ordenes_pago_anuladas']:
        total_anuladas += float(orden_pago_detalle['total'])

    total = {'punto_emision_uaa': punto_emision_uaa['descripcion'],
             'total_forma_pago': total_formas_pago,
             'total_emitidas': format(round(total_emitidas, 2), '.2f'),
             'total_anuladas': format(round(total_anuladas,2), '.2f')}

    totales.append(total)
    return total

def get_puntos_emision_total(totales, tipo):
    sumatoria=0
    for total in totales:
        sumatoria+= float(total[tipo])
    return format(round(sumatoria,2), '.2f')

def get_forma_pago_total(totales, form_pago):
    sumatoria=0
    for total in totales:
        sumatoria += total['total_forma_pago'][form_pago]
    return sumatoria

def get_detalle_subtotal(orden_pago_detalle):
    subtotal=float(orden_pago_detalle['cantidad'])*float(orden_pago_detalle['precio'])
    return format(round(subtotal,2), '.2f')


def get_formato_secuencial_orden_pago_detalle(secuencial):
    return "%012d" % secuencial

def get_fecha(fecha):
    fstr = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S")
    return fstr

def get_valor_diccionario(dict, key):
    return dict[key]

register.simple_tag(get_total_documentos)
register.simple_tag(get_detalle_subtotal)
register.simple_tag(get_punto_emision_total)
register.simple_tag(get_puntos_emision_total)
register.simple_tag(get_forma_pago_total)
register.simple_tag(get_formato_secuencial_orden_pago_detalle)
register.simple_tag(get_fecha)
register.simple_tag(get_valor_diccionario)