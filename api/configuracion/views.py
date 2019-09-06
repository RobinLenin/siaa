from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.configuracion.serializers import *

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def detalle_parametrizacion_lista_por_padre(request):
    """
    Retorna una lista de detalle de parametrización de
    acuerdo al codigo de la Parametrización padre.
    :param request:
    :return:
    """
    queryset = DetalleParametrizacion.objects.filter(parametrizacion__codigo=request.query_params['codigo']).all()
    serializer = DetalleParametrizacionSerializer(queryset, many=True)
    return Response({'data': serializer.data,
                     'status': status.HTTP_200_OK,
                     'message': None})


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def detalle_parametrizacion_por_codigo(request):
    """
    Permite devolver un detalle de parametrizacion de acuerdo a su codigo
    :param request:
    :return:
    """
    try:
        codigo = request.query_params['codigo']
        queryset = DetalleParametrizacion.objects.filter(codigo=codigo).first()
        serializer = DetalleParametrizacionSerializer(queryset)
        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': ''})
    except Exception as e:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error en el servicio'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
