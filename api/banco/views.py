from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.recaudacion.models import OrdenPago, PuntoEmisionUAA, Pago


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def pago_abonar(request):
    """
    Registra la orden de pago ha estado de EMITIDA y depósito por código de la solicitud. El punto de emisión es igual
    al codigo de la solicitud
    :param request: {"estudiante_codigo": "1105039059","identificación": "1105039059", "institucion_codigo": "001",
    "curso_codigo": "1","valor_total": 15,"fecha_pago": "2019-01-01 13:00:00","secuencia_banco": "1"}
    :return:
    200 Exito {'secuencia_banco': '', 'secuencia_unl': '', 'estudiante_codigo': '', 'valor_pagado': ''}
    400 Error solicitud, por que el pago no existe, ya se ha cancelado, la fecha de vencimiento ha caducado si existe o
    el valor que envia el banco es diferente al valor a cancelar {'error_codigo': 400, 'error_descripcion': ''}
    """
    try:
        data = request.data
        punto_emision_uaa = PuntoEmisionUAA.objects.filter(codigo=data['institucion_codigo']).first()
        if punto_emision_uaa:
            orden_pago = OrdenPago.objects.get(id=data['curso_codigo'],
                                               persona__numero_documento=data['identificación'])
            if orden_pago.estado == orden_pago.ESTADO_PENDIENTE:
                if orden_pago.fecha_vencimiento is None or (
                        orden_pago.fecha_vencimiento and orden_pago.fecha_vencimiento >= datetime.now()):
                    if round(float(orden_pago.total), 2) == round(float(data['valor_total']), 2):
                        # Guardo el pago
                        pago = Pago()
                        pago.forma_pago = pago.FORMA_PAGO_DEPOSITO_CODIGO
                        pago.total = orden_pago.total
                        pago.referencia = data['secuencia_banco']
                        pago.fecha_pago = datetime.strptime(data['fecha_pago'], '%Y-%m-%d %H:%M:%S')
                        pago.save()
                        # Actualizo la orden de pago
                        orden_pago.pago = pago
                        orden_pago.punto_emision_uaa = punto_emision_uaa
                        orden_pago.estado = orden_pago.ESTADO_EMITIDA
                        for item in orden_pago.ordenes_pago_detalle.all():
                            item.secuencial = punto_emision_uaa.new_secuencial_orden_pago_detalle()
                            item.estado = orden_pago.ESTADO_EMITIDA
                            item.save()
                            punto_emision_uaa.actualizar_secuencial()
                        orden_pago.save()

                        return Response({'secuencia_banco': orden_pago.pago.referencia,
                                         'secuencia_unl': orden_pago.id,
                                         'estudiante_codigo': orden_pago.persona.numero_documento,
                                         'valor_pagado': orden_pago.pago.total})
                    else:
                        error_descripcion = 'El valor a cancelar %s difiere del pago recibido %s' % (
                            str(orden_pago.total), data['valor_total'])
                else:
                    error_descripcion = 'Registro con fecha de vencimiento caducado %s' % (orden_pago.fecha_vencimiento)
            else:
                error_descripcion = 'El registro ya se encuentra en estado de pago %s' % (orden_pago.estado)
        else:
            error_descripcion = 'No existe el punto de emisión UAA con código=%s' % (data['institucion_codigo'])

    except OrdenPago.DoesNotExist:
        error_descripcion = 'Registro no encontrado en el Servidor'

    except Exception as e:
        error_descripcion = str(e)

    error_codigo = status.HTTP_400_BAD_REQUEST

    return Response(data={'error_codigo': error_codigo,
                          'error_descripcion': error_descripcion},
                    status=error_codigo)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def pago_lista(request, identificacion, codigo_institucion):
    """
    Lista todos las ordenes de pago que debe cancelar una persona (PENDIENTE)
    :param request:
    :param identificacion: numero de documento de la persona
    :param codigo_institucion: este codigo es igual para todos los registros, util para el método de abonar
    :return:
    [{"curso_codigo": "1","curso_descripcion": "Formación continua, curso ingles","estudiante_codigo": "1105039059",
      "estudiante_nombre": "Fernanda Lopez","identificacion": "1105039059","referencia": "01.500",
      "referencia_auxiliar": "1","valor_curso": 15,"valor_recargo": 0,
      "valor_total": 15,"fecha_vencimiento": null},.....]
    """
    datos = []
    ordenes_pago = OrdenPago.objects.filter(persona__numero_documento=identificacion,
                                            estado=OrdenPago.ESTADO_PENDIENTE,
                                            pago__isnull=True).all()

    for orden_pago in ordenes_pago:
        item = {"curso_codigo": orden_pago.id,
                "curso_descripcion": orden_pago.descripcion,
                "estudiante_codigo": orden_pago.persona.numero_documento,
                "identificacion": orden_pago.persona.numero_documento,
                "estudiante_nombre": orden_pago.persona.get_nombres_completos(),
                "referencia": orden_pago.referencia,
                "referencia_auxiliar": orden_pago.referencia_externa,
                "valor_curso": orden_pago.total,
                "valor_recargo": 0,
                "valor_total": orden_pago.total,
                "codigo_institucion": codigo_institucion,
                "fecha_vencimiento": datetime.strftime(orden_pago.fecha_vencimiento,
                                                       '%Y-%m-%d %H:%M:%S') if orden_pago.fecha_vencimiento else None
                }
        datos.append(item)

    return Response(data=datos)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def pago_reverso(request, secuencia_banco, secuencia_unl):
    """
    Cancela la orden de pago (reverso)
    :param request:
    :param secuencia_banco: Generado por el banco
    :param secuencia_unl: Generado por la Unl, id de la orden de pago
    :return:
    200 Exito, {'secuencia_banco': '','secuencia_unl': ''}
    400 Error solicitud, por que el pago no existe, esta pendiente o ya ha sido cancelado {'error_codigo': 400, 'error_descripcion': ''}
    """
    try:
        orden_pago = OrdenPago.objects.get(pago__referencia=secuencia_banco, id=secuencia_unl)
        if orden_pago.estado == orden_pago.ESTADO_EMITIDA:

            orden_pago.estado = orden_pago.ESTADO_ANULADA
            orden_pago.pago.fecha_reverso = datetime.now()
            orden_pago.save()
            orden_pago.pago.save()
            orden_pago.ordenes_pago_detalle.update(estado=orden_pago.ESTADO_ANULADA)

            return Response({'secuencia_banco': orden_pago.pago.referencia,
                             'secuencia_unl': orden_pago.id})
        else:
            if orden_pago.estado == orden_pago.ESTADO_ANULADA:
                error_descripcion = 'Registro ya ha sido ANULADO con fecha %s' % (
                    datetime.strftime(orden_pago.pago.fecha_reverso, '%Y-%m-%d %H:%M:%S'))
            else:
                error_descripcion = 'Registro en estado de pago %s' % (orden_pago.estado)

    except OrdenPago.DoesNotExist:
        error_descripcion = 'Registro no encontrado en el Servidor'

    error_codigo = status.HTTP_400_BAD_REQUEST

    return Response(data={'error_codigo': error_codigo,
                          'error_descripcion': error_descripcion},
                    status=error_codigo)
