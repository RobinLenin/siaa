from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.http import HttpResponseServerError, HttpResponseNotFound

from app.core.utils.ldap import autenticar_by_uid_or_targetedID, modificar_password_by_uid_ldap, consultar_informacion_ldap


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def autenticar_usuario(request, user_name, password):
    """
    Metodo llamado desde el sga-docentes para authenticar con ldap
    :param request: user_name
    :param request: password
    :return:
    """
    try:
        valid_info = autenticar_by_uid_or_targetedID(user_name, password)
        if valid_info:
            print(valid_info)
            #valid_info["status"]="ok"
            #valid_info["message"] = ""
            return Response(valid_info)
        return HttpResponseNotFound('error')
    except Exception as ex:
        return HttpResponseServerError(str(ex))

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def cambiar_password(request, user_name, password):
    """
    Metodo llamado desde el sga-docentes para cambiar contraseña con ldap
    :param request: user_name
    :param request: password
    :return:
    """
    try:
        valid_info = modificar_password_by_uid_ldap(user_name, password)
        if valid_info:
            return Response('ok')
        return HttpResponseNotFound('error')
    except Exception as ex:
        return HttpResponseServerError(str(ex))

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def consultar_informacion(request, user_name):
    """
    Metodo llamado desde el sga-docentes para authenticar con ldap
    :param request: user_name
    :param request: password
    :return:
    """
    try:
        valid_info = consultar_informacion_ldap(user_name)
        if valid_info:
            print(valid_info)
            #valid_info["status"]="ok"
            #valid_info["message"] = ""
            return Response(valid_info)
        return HttpResponseNotFound('error')
    except Exception as ex:
        return HttpResponseServerError(str(ex))