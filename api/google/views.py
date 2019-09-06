from django.http import HttpResponseServerError, HttpResponseNotFound
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from app.core.utils.google import get_usuario


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def validar_correo(request, correo):
    """
    Metodo llamado desde el sga para comprobar si el correo existe
    :param request: email
    :return:
    """
    try:
        if correo.endswith('@unl.edu.ec'):
            nombre, sufijo = correo.split('@')
            res = get_usuario(nombre)
            if res:
                return Response('ok')
        return HttpResponseNotFound('error')
    except Exception as ex:
        return HttpResponseServerError(str(ex))
