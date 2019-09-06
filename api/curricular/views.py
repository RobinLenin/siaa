from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.curricular.serializers import CarreraSerializer
from app.curricular.models import Carrera


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def carrera_lista_vigentes(request):
    """
    Retorna lista de carreras vigentes
    :param request:
    :return:
    """
    try:
        queryset = Carrera.objects.filter(vigente=True)
        serializer = CarreraSerializer(queryset, many=True)
        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': None})
    except Exception as e:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error en el servicio'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
