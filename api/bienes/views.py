# Proyecto:siaa
# Autor   : Yazber Romero
# Fecha   :08/06/16 15:20

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.bienes.serializers import *
from app.core.utils.general import api_paginacion


@api_view(['PUT'])
@renderer_classes((JSONRenderer,))
def detalle_prestacion_guardar(request, id):
    """
    Permite Editar detalle de la prestacion
    :param request:
    :param id:
    :param token:
    :return:
    """
    try:
        item = DetallePrestacion.objects.get(id=id)
        item.persona_id = request.data['persona_id']
        item.carrera_id = request.data['carrera_id']
        item.razon_id = request.data['razon_id']
        item.estado_id = request.data['estado_id']
        item.funcion_id = request.data['funcion_id']
        item.hora_entrada = request.data['hora_entrada']
        item.hora_salida = request.data['hora_salida']
        item.fecha_registro = request.data['fecha_registro']
        item.fecha_finalizacion = request.data['fecha_finalizacion']
        item.numero = request.data['numero']
        item.tipo_ente_id = request.data['tipo_ente_id']

        serializer = DetallesPrestacionSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'data': serializer.data,
                             'status': status.HTTP_200_OK,
                             'mensaje': 'Se ha actualizado Detalle de Prestacion Satisfactoriamente'})

        return Response({'mensaje': 'Error al actualizar Detalle de Prestaciones',
                         'status': status.HTTP_400_BAD_REQUEST})

    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def detalle_prestacion_lista(request):
    """
    Lista todas los detalles de prestaciones paginado
    :param request:
    :return:
    """
    try:
        queryset = DetallePrestacion.objects.filter(activo=True, prestacion__usuario_id=request.user.id)
        filter = request.GET.get('filter')
        if filter:
            queryset = DetallePrestacion.buscar(filter)
        page = request.GET.get('page')
        numero_items_por_pagina = request.GET.get('numberItems')
        detalle_prestaciones = api_paginacion(queryset, page, numero_items_por_pagina)
        serializer = DetallesPrestacionSerializer(detalle_prestaciones, many=True)
        return Response(
            {'status': status.HTTP_200_OK, 'data': serializer.data, 'message': '', 'count': queryset.count()})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Error en el servicio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def detalle_prestacion_filtro(request, fechaDesde, fechaHasta):
    """
    Obtiene los detalles prestaciones de acuerdo a una fecha de inicio y fin
    :param request:
    :param fechaDesde:
    :param fechaHasta:
    :return:
    """
    try:
        queryset = DetallePrestacion.objects.filter(fecha_registro__range=[fechaDesde, fechaHasta], activo=True)
        serializer = DetallesPrestacionSerializer(queryset, many=True)
        return Response({'status': status.HTTP_200_OK, 'data': serializer.data, 'message': ''})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Error en el servicio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def prestacion_guardar(request, token):
    """
    Permite Ccrear-Editar Prestacion con sus detalles
    :param request:
    :param token:
    :return:
    """
    try:
        t = Token.objects.get(key=token)
        prestacion = Prestacion()
        prestacion.usuario_id = t.user.id
        prestacion.tipo_id = request.data['tipo_id']
        serializer = PrestacionSerializer(prestacion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            for detalle in request.data['detalles']:
                if detalle['id'] is None:
                    item = DetallePrestacion()
                    item.prestacion_id = prestacion.id
                    item.persona_id = detalle['persona_id']
                    item.carrera_id = detalle['carrera_id']
                    item.razon_id = detalle['razon_id']
                    item.estado_id = detalle['estado_id']
                    item.funcion_id = detalle['funcion_id']
                    item.hora_entrada = detalle['hora_entrada']
                    item.hora_salida = detalle['hora_salida']
                    item.fecha_registro = detalle['fecha_registro']
                    item.fecha_finalizacion = detalle['fecha_finalizacion']
                    item.numero = detalle['numero']
                    item.tipo_ente_id = detalle['tipo_ente_id']
                    item.save()

            return Response(
                {'data': serializer.data, 'status': status.HTTP_200_OK,
                 'mensaje': 'Se ha grabado Prestacion Satisfactoriamente'})

        return Response(
            {'mensaje': 'Error al grabar Prestacion',
             'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Error en el servicio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

