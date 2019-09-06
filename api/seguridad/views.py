from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.seguridad.serializers import UsuarioPersonaSerializer

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def usuario_logueado(request):
    """
    Devuelve los datos del usuario autenticado
    :param request:
    :param key:
    :return:
    """
    serialized = UsuarioPersonaSerializer(request.user)
    return Response(serialized.data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def usuario_logueado_funcionalidades(request):
    """
    Obtiene las funcionalidades a las que tiene acceso el usuario autenticado respecto a las
    funcionalidades de angular
    """
    funcionalidades = request.user.funcionalidades_angular()
    return Response(funcionalidades)