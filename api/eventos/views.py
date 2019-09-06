from datetime import datetime

import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.sga.utils import WebServiceSga
from app.configuracion.models import DetalleParametrizacion
from app.core.models import Persona, CatalogoItem, Direccion
from app.core.utils.general import dividir_nombres_completos
from app.recaudacion.models import OrdenPago, Producto, OrdenPagoDetalle


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def consultar_persona(request, numero_documento):
    """
    Retorna los datos principales de una persona, con su dirección de domicilio y si es estudiante o docente actual en
    el SGA con los id de las carreras a las que pertenece
    :param request:
    :param numero_documento:
    :return:
    200 Exito {'persona': {...}, 'direccion': {...}, 'estudiante': [], 'docente': []}
    400 Error solicitud, con su descripción
    """
    try:
        datos = {}
        # Existe la persona en el Siaaf
        persona = Persona.objects.filter(numero_documento=numero_documento).first()
        if persona is not None:
            datos['persona'] = {'numero_documento': persona.numero_documento,
                                'primer_nombre': persona.primer_nombre,
                                'segundo_nombre': persona.segundo_nombre,
                                'primer_apellido': persona.primer_apellido,
                                'segundo_apellido': persona.segundo_apellido,
                                'correo_electronico': persona.correo_electronico,
                                'tipo_documento': {
                                    'nombre': persona.tipo_documento.nombre,
                                    'codigo_th': persona.tipo_documento.codigo_th},
                                'sexo': {
                                    'nombre': persona.sexo.nombre,
                                    'codigo_th': persona.sexo.codigo_th}
                                }
            direccion = persona.get_direccion_domicilio()
            if direccion:
                datos['direccion'] = {
                    'celular': direccion.celular,
                    'telefono': direccion.telefono,
                    'calle_principal': direccion.calle_principal,
                    'calle_secundaria': direccion.calle_secundaria,
                    'numero': direccion.numero
                }
            else:
                datos['direccion'] = {
                    'celular': None,
                    'telefono': None,
                    'calle_principal': None,
                    'calle_secundaria': None,
                    'numero': None
                }

        # No existe la persona, lo busca en el registro civil
        else:
            headers = {'content-type': "application/x-www-form-urlencoded",
                       'cache-control': "no-cache",
                       'charset': "utf-8"}
            url_siaaf = DetalleParametrizacion.get_detalle_parametrizacion('SIAAF', 'SIAAF_URL_PRODUCCION')
            url_bsg = '%s/api/v1/bsg/consultar-cedulasss/%s' % (url_siaaf.valor, numero_documento)
            response = requests.request("GET", url_bsg, headers=headers)

            if response.status_code == 200:
                data = response.json()['data']
                if data and data.get('CodigoError') == '000':
                    sexo_ref = {'HOMBRE': 1, 'MUJER': 0}
                    sexo = CatalogoItem.get_catalogo_item('TIPO_SEXO', sexo_ref.get(data.Sexo, 1))
                    tipo_documento = CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO', 1)
                    primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = dividir_nombres_completos(
                        data.get('Nombre'))

                    datos['persona'] = {'numero_documento': data.get('NUI'),
                                        'primer_nombre': primer_nombre,
                                        'segundo_nombre': segundo_nombre,
                                        'primer_apellido': primer_apellido,
                                        'segundo_apellido': segundo_apellido,
                                        'correo_electronico': None,
                                        'tipo_documento': {
                                            'nombre': tipo_documento.nombre,
                                            'codigo_th': tipo_documento.codigo_th},
                                        'sexo': {
                                            'nombre': sexo.nombre,
                                            'codigo_th': sexo.codigo_th},
                                        }
                    datos['direccion'] = {
                        'celular': None,
                        'telefono': None,
                        'calle_principal': data.get('Calle', None),
                        'calle_secundaria': None,
                        'numero': data.get('NumeroCasa', None)
                    }

        # Obtengo las carreras actuales si es estudiante o docente (SGA)
        if 'persona' in datos:
            data = WebServiceSga.get_sgaws_datos_usuario_koha(numero_documento)
            datos['estudiante'] = [{'id': dato['id'], 'carrera': dato['nombre']} for dato in
                                   data['carreras_estudiante']] if data else []
            datos['docente'] = [{'id': dato['id'], 'carrera': dato['nombre']} for dato in
                                data['carreras_docente']] if data else []

        return Response(data=datos)

    except Exception as e:
        datos = str(e)

    return Response(data={'detail': datos},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def orden_pago_estado(request, id):
    """
    Retorna el estado de una orden de pago
    :param request:
    :param id: id de la orden de pago
    :return:
    200 Exito {'orden_pago_id': '10', 'referencia_externa': '5', 'estado': 'PENDIENTE',
    'forma_pago': null, 'referencia_pago': null, 'fecha_pago': null}
    404 Registro no encontrado,
    """
    orden_pago = get_object_or_404(OrdenPago, id=id)
    data = {'orden_pago_id': orden_pago.id,
            'referencia_externa': orden_pago.referencia_externa,
            'estado': orden_pago.estado,
            'forma_pago': orden_pago.pago.forma_pago if orden_pago.pago else None,
            'referencia_pago': orden_pago.pago.referencia if orden_pago.pago else None,
            'fecha_pago': datetime.strftime(orden_pago.pago.fecha_pago,
                                            '%Y-%m-%d %H:%M:%S') if orden_pago.pago else None
            }
    return Response(data=data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def orden_pago_guardar(request):
    """
    Guarda la orden de pago en estado de PENDIENTE y sin registro de Pago
    "persona" : {
        "numero_documento": "1105039059(*)", "primer_nombre": "Lissette(*)",
        "segundo_nombre": "Geoconda", "primer_apellido": "Lopez (*)",
        "segundo_apellido": "Faican", "correo_electronico": "lissette.lopez@unl.edu.ec (*)",
        "tipo_documento": {"nombre": "Cédula(*)","codigo_th": "1(*)"},
        "sexo": { "nombre": "Mujer(*)","codigo_th": "0(*)"}
    },
    "direccion" : {
        "calle_principal": "Av. Chuquiribamba(*)",  "numero": "sn",
        "calle_secundaria": "Lago Michigan","celular": "0989170671(*)", "telefono": ""
    },
    "orden_pago" : {
        "descripcion": "Nombre del evento (*)", "referencia": "Sistema de eventos",
        "referencia_externa": "id del evento (*)", "total": 25 (*)
    }
    :param request:
    :return:
    200 Exito {'orden_pago_id': 10, 'estado': 'PENDIENTE'}
    400 Error solicitud, con su descripción
    """
    try:
        persona = request.data.get('persona')
        direccion = request.data.get('direccion')
        orden_pago = request.data.get('orden_pago')
        # Obtengo los registros que son necesarios, catalogos items y el producto para la orden de pago
        tipo_documento = CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO', persona['tipo_documento']['codigo_th'])
        sexo = CatalogoItem.get_catalogo_item('TIPO_SEXO', persona['sexo']['codigo_th'])
        tipo_direccion = CatalogoItem.get_catalogo_item('TIPO_DIRECCION', 2)

        # Obtengo el codigo del producto por parametrización. Posterior, se puede asociar un codigo del producto
        # por id del evento (referencia_externa)
        detalle = DetalleParametrizacion.get_detalle_parametrizacion('RECAUDACION', 'EVENTOS_CODIGO_PRODUCTO')
        codigo = detalle.valor
        producto = Producto.objects.filter(codigo=codigo).first()

        if tipo_documento and sexo and tipo_direccion and producto:

            # Guardo la persona y direccion
            persona.update({'sexo': sexo, 'tipo_documento': tipo_documento})
            persona_obj, create = Persona.objects.update_or_create(numero_documento=persona['numero_documento'],
                                                                   defaults=persona)

            direccion_obj, create = Direccion.objects.update_or_create(tipo_direccion=tipo_direccion,
                                                                       persona=persona_obj,
                                                                       defaults=direccion)

            if persona_obj and direccion_obj:
                # Genero la orden pago
                orden_pago_obj = OrdenPago()
                orden_pago_obj.fecha_emision = datetime.now()
                orden_pago_obj.persona = persona_obj
                orden_pago_obj.direccion = direccion_obj
                orden_pago_obj.descripcion = orden_pago['descripcion']
                orden_pago_obj.referencia = orden_pago.get('referencia', None)
                orden_pago_obj.referencia_externa = orden_pago['referencia_externa']
                orden_pago_obj.total = orden_pago['total']

                # Genero la orden pago detalle
                cantidad = 1
                precio = round(orden_pago_obj.total / (float(producto.tipo_impuesto.valor) + 1), 2)
                impuesto = round(orden_pago_obj.total - precio, 2)
                total = round(precio + impuesto, 2)

                detalle_obj = OrdenPagoDetalle()
                detalle_obj.cantidad = cantidad
                detalle_obj.impuesto = impuesto
                detalle_obj.precio = precio
                detalle_obj.total = total
                detalle_obj.producto = producto
                detalle_obj.producto_codigo = producto.codigo
                detalle_obj.producto_descripcion = producto.descripcion
                detalle_obj.tipo_impuesto = producto.tipo_impuesto
                detalle_obj.impuesto_tarifa = producto.tipo_impuesto.valor
                detalle_obj.impuesto_codigo = producto.tipo_impuesto.codigo

                # Guardo los registros
                orden_pago_obj.save()
                detalle_obj.orden_pago = orden_pago_obj
                detalle_obj.save()

                return Response(data={'orden_pago_id': orden_pago_obj.id,
                                      'estado': orden_pago_obj.estado})

            else:
                datos = 'Error al guardar la persona y dirección'
        else:
            datos = 'No existen los catalogs items (codigo_th) o el producto (descripción) para la orden de pago'

    except Exception as e:
        datos = str(e)

    return Response(data={'detail': datos},
                    status=status.HTTP_400_BAD_REQUEST)
