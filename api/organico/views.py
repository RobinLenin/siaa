from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.organico.serializers import UAASerializer
from app.organico.models import UAA


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def uaa_lista_padres(request):
    """
    Obtiene todas las Unidades Académicas Administrativas que no son hijas (Nivel superior)
    """
    try:
        uaas = UAA.objects.filter(uaa=None).all()
        serializer = UAASerializer(uaas, many=True)
        # Retorna un campo que determina si es padre o no
        for uaa in serializer.data:
            uaa['es_padre'] = False if UAA.objects.filter(uaa__id=uaa['id']).count() == 0 else True

        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': None})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def uaa_lista_hijas(request):
    """
    Obtiene todas las Unidades Académicas Administrativas hijas relacionada a la uaa pasada como parametro
    """
    try:
        id_uaa_padre = request.GET['id_uaa_padre']
        uaas = UAA.objects.filter(uaa__id=id_uaa_padre).all()
        serializer = UAASerializer(uaas, many=True)
        # Retorna un campo que determina si es padre o no
        for uaa in serializer.data:
            uaa['es_padre'] = False if UAA.objects.filter(uaa__id=uaa['id']).count() == 0 else True

        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': None})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
