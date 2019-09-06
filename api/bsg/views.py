import re
from builtins import print

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from app.bsg import views


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def consultar_registrocivil_por_cedula(request, cedula):
    """
    Servicio que permite retornar en los datos una persona en el registro civil
    :param request:
    :param cedula:
    :return: Devuelve un dict con los datos personales del propietario de la cedula ingresada como parámetro
    """
    try:
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        response = views.consultar_por_cedula_regciv(cedula, force)
        if response is None or response == "":
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "error",
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': status.HTTP_200_OK, 'data': response})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def consultar_registrocivil_por_nombres(request):
    """
    Servicio que permite retornar los datos una persona en el registro civil buscado por nombres y apellidos
    :param request:
    :return:
    """
    try:
        primer_nombre = request.GET.get('primer_nombre')
        segundo_nombre = request.GET.get('segundo_nombre')
        primer_apellido = request.GET.get('primer_apellido')
        segundo_apellido = request.GET.get('segundo_apellido')
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        response = views.consultar_por_nombre_regciv(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                                                     force)
        if response is None or response == "":
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "error",
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': status.HTTP_200_OK, 'data': response})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def consultar_discapacidad_por_cedula(request, cedula):
    """
    Método que permite retornar los datos de una persona con discapacidad del Ministerio de Salud Pública
    :param request:
    :param cedula:
    :return: Devuelve un dict con los datos personales e informacion de discapacidad del propietario de la cédula
    que se ingresa como parámetro.
    """
    try:
        if cedula is None:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': u"Por favor ingresar un numero de identificacion",
            }, status=status.HTTP_400_BAD_REQUEST)
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        response = views.consultar_discapacidad_msp(cedula, force)
        if response is None:
            return Response({
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': "error",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': status.HTTP_200_OK, 'data': response})
    except Exception as e:

        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def consultar_titulos_por_cedula(request, cedula):
    """
    Método que permite retornar los datos de titulos registrados en el SENESCYT de un Titulado.
    :param request:
    :param cedula:
    :return: Devuelve un dict con la información de los titulos registrados en el SENESCYT del propietario de la cedula.
    """
    try:
        if cedula is None:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': u"Por favor ingresar un numero de identificacion",
            }, status=status.HTTP_400_BAD_REQUEST)
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        response = views.consultar_titulos_senescyt(cedula, force)

        if response is None or response == "":
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': u'No se ha podido recuperar los titulos. Verifique que la cedula sea correcta.',
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': status.HTTP_200_OK, 'data': response})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def consultar_registrocivil_all_cedulas(request):
    """
    Método que recibe un texto de cédulas (pueden estar separadas por coma, punto y coma, espacio, salto de linea) y retorna los datos consumidos del registro civil
    :param request: texto que contiene una lista de cédulas
    :return: Devuelve una lista con los datos personales del propietario de la cedula
    """
    try:
        data = []
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        cedulas = request.data

        pattern = re.compile(",|;|[\t]|[\n]|[\r]|[\s]")
        lista_cedulas = pattern.split(cedulas)
        lista_cedulas = [split for split in lista_cedulas if split != ""]

        for cedula in lista_cedulas:
            response = views.consultar_por_cedula_regciv(cedula, force)
            print('respuesta', cedula, response)
            if response is None or response == "":
                response = {'NUI': cedula,
                            'Error': u'No se ha podido recuperar los datos. Verifique que la cedula sea correcta.'}
            data.append(response)

        return Response({'status': status.HTTP_200_OK, 'data': data})

    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def consultar_discapacidades_all_cedulas(request):
    """
    Método que recibe un texto de cédulas (pueden estar separadas por coma, punto y coma, espacio, salto de linea) y retorna una lista de personas con información de discapacidad del Ministerio de Salud Pública
    :param request: texto que contiene una lista de cédulas
    :return: Devuelve una lista con los datos personales e informacion de discapacidad del propietario de la cédula.
    """

    try:
        data = []
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        cedulas = request.data

        pattern = re.compile(",|;|[\t]|[\n]|[\r]|[\s]")
        lista_cedulas = pattern.split(cedulas)
        lista_cedulas = [split for split in lista_cedulas if split != ""]

        for cedula in lista_cedulas:
            response = views.consultar_discapacidad_msp(cedula, force)
            print('respuesta', cedula, response)
            if response is None or response == "":
                response = {'NumeroIdentificacion': cedula,
                            'Error': u'No se ha podido recuperar la discapacidad. Verifique que la cedula sea correcta.'}
            else:
                response.NumeroIdentificacion = cedula

            data.append(response)

        return Response({'status': status.HTTP_200_OK, 'data': data})

    except Exception as e:

        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def consultar_titulos_all_cedulas(request):
    """
    Método que recibe un texto de cédulas (pueden estar separadas por coma, punto y coma, espacio, salto de linea)  y retornar los datos de titulos registrados en el SENESCYT.
    :param request: texto que contiene una lista de cédulas
    :return: Devuelve una lista con la información de los titulos registrados en el SENESCYT del propietario de la cedula.
    """
    try:

        data = []
        force = False if 'force' not in request.GET else True if request.GET['force'] in ['true', 'True'] else False
        cedulas = request.data

        pattern = re.compile(",|;|[\t]|[\n]|[\r]|[\s]")
        lista_cedulas = pattern.split(cedulas)
        lista_cedulas = [split for split in lista_cedulas if split != ""]

        for cedula in lista_cedulas:
            response = views.consultar_titulos_senescyt(cedula, force)
            print('respuesta', cedula, response)
            if response is None or response == "":
                response = {'numeroIdentificacion': cedula,
                            'message': u'No se ha podido recuperar los titulos. Verifique que la cedula sea correcta.'}
            data.append(response)

        return Response({'status': status.HTTP_200_OK, 'data': data})

    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': e,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
