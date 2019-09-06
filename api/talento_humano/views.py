# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.decorators import list_route, api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.talento_humano.serializers import FuncionarioPersonaSerializer
from app.talento_humano.models import Funcionario


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@list_route()
def funcionario_lista(request):
    """
    Retorna un diccionario con la lista de funcionarios mostrando datos principales de la persona,
    estado de la petición y mensaje
    :param request:
    :return:
    """
    queryset = Funcionario.objects.all().order_by('usuario__persona__primer_apellido',
                                                  'usuario__persona__segundo_apellido',
                                                  'usuario__persona__primer_nombre',
                                                  'usuario__persona__segundo_nombre', )
    serializer = FuncionarioPersonaSerializer(queryset, many=True)
    return Response({'data': serializer.data,
                     'status': status.HTTP_200_OK,
                     'message': None })
