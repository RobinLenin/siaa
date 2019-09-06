import requests
from rest_framework import status
from rest_framework.decorators import renderer_classes, api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.core.serializers import *
from app.configuracion.models import DetalleParametrizacion
from app.core.models import *
from app.core.utils.general import api_paginacion

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def catalogo_item_por_codigo(request):
    """
    Permite obtener un catálogo item en base a su codigo(unico)
    :param request:
    :return:
    """
    try:
        codigo = request.query_params['codigo']
        catalogoItem = CatalogoItem.objects.filter(activo=True, codigo_th=codigo).first()
        serializer = CatalogoItemSerializer(catalogoItem)
        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': ''})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Error en el servicio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def catalogo_item_lista_por_catalogo(request):
    """
    Obtiene los catalogos items por el codigo del catalogo padre
    :param request:
    :return:
    """
    try:
        codigo_catalogo = request.query_params['codigoCatalogo']
        catalogo_items = CatalogoItem.objects.filter(activo=True,
                                                     catalogo__codigo=codigo_catalogo).order_by('orden')
        serializer = CatalogoItemRecursivoSerializer(catalogo_items, many=True)
        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': ''})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Error en el servicio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def canton_lista_por_provincia(request):
    """
    Retorna todas las cantones de una provincia, estado de la petición y mensaje.
    :param request:
    :return:
    """
    cantones = Canton.objects.filter(provincia__id=request.query_params['provincia_id'])
    serializer = CantonSerializer(cantones, many=True)
    return Response({'status': status.HTTP_200_OK,
                     'data': serializer.data})


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def pais_lista(request):
    """
    Retorna todas los paises, estado de la petición y mensaje.
    :param request:
    :return:
    """
    try:
        queryset = Pais.objects.all()
        serializer = PaisSerializer(queryset, many=True)
        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data})
    except Exception as e:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error en el servicio'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def provincia_lista_por_pais(request):
    """
    Retorna todas las provincias de un pais, estado de la petición y mensaje.
    :param request:
    :return:
    """
    provincias = Provincia.objects.filter(pais__id=request.query_params['pais_id'])
    serializer = ProvinciaSerializer(provincias, many=True)
    return Response({'status': status.HTTP_200_OK,
                     'data': serializer.data})


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def parroquia_lista_por_canton(request):
    """
    Retorna todas las parroquias de una canton, estado de la petición y mensaje.
    :param request:
    :return:
    """
    parroquias = Parroquia.objects.filter(canton__id=request.query_params['canton_id'])
    serializer = ParroquiaSerializer(parroquias, many=True)
    return Response({'status': status.HTTP_200_OK,
                     'data': serializer.data})

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def parroquia_lista(request):
    """
    Retorna todas las parroquias con la información de canton, provincia y pais, estado de la petición y mensaje.
    :param request:
    :return:
    """
    parroquias = Parroquia.objects.all().values('id', 'nombre', 'canton__nombre', 'canton__provincia__nombre', 'canton__provincia__pais__nombre')
    return Response({'status': status.HTTP_200_OK,
                     'data': parroquias})

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def persona_o_registrocivil(request):
    """
    Retorna la persona si existe o retorna los datos del registro civil segun el número de identificación
    :param request:
    :return:
    """
    try:
        numero_documento = request.query_params['numero_documento']
        persona = Persona.objects.filter(numero_documento=numero_documento).first()

        # Existe la persona en el Siaaf
        if persona is not None:
            return Response({'data': PersonaSerializer(persona).data,
                             'status': status.HTTP_200_OK,
                             'message': None})
        # Persona es None, lo busca en el registro civil
        else:
            headers = {'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache",
                       "charset": "utf-8"}
            url_siaaf = DetalleParametrizacion.get_detalle_parametrizacion('SIAAF', 'SIAAF_URL_PRODUCCION')
            url_bsg = '%s/api/v1/bsg/consultar-cedula/%s?force=False' % (
            url_siaaf.valor, numero_documento)
            response = requests.request("GET", url_bsg, headers=headers)

            if response.status_code == 200:
                data = response.json()['data']
                if data and data.get('CodigoError') == '000':
                    persona = Persona()
                    primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = dividir_nombres_completos(data.get('Nombre'))
                    persona.primer_nombre = primer_nombre
                    persona.segundo_nombre = segundo_nombre
                    persona.primer_apellido = primer_apellido
                    persona.segundo_apellido = segundo_apellido
                    persona.numero_documento = data.get('NUI')
                    persona.profesion = data.get('Profesion', None)
                    persona.fecha_nacimiento = datetime.datetime.strptime(data.get('FechaNacimiento'),
                                                                             '%d/%m/%Y').date()
                    persona.tipo_documento = CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO', 1)
                    persona.sexo = CatalogoItem.get_catalogo_item('TIPO_SEXO',
                                                                  0 if data.get('Sexo', None) == 'MUJER' else 1)

                    personaSerializer = PersonaSerializer(persona).data
                    personaSerializer['Calle'] = data.get('Calle', None)
                    personaSerializer['NumeroCasa'] = data.get('NumeroCasa', None)

                    return Response({'data': personaSerializer,
                                     'status': status.HTTP_200_OK,
                                     'message': None})

                else:
                    message = data.get('Error', 'Persona no encontrada')
            else:
                message = "Error al consultar del registro civil"

            return Response({'data': None,
                             'status': status.HTTP_200_OK,
                             'message': message})
    except:
        return Response({'data': None,
                         'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': None})

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def persona_lista_paginacion(request):
    """
    Retorna un diccionario con la lista de personas segun la
    paginación, estado de la petición y un mensaje
    :param request:
    :return:
    """
    try:
        filter = request.query_params['filter']
        page = request.query_params['page']
        numero_items_por_pagina = request.query_params['numberItems']
        queryset = Persona.objects.all()
        if filter:
            queryset = Persona.buscar(filter)
        personas = api_paginacion(queryset, page, numero_items_por_pagina)
        serializer = PersonaSerializer(personas, many=True)
        return Response({'status': status.HTTP_200_OK,
                         'data': serializer.data,
                         'message': '',
                         'count': queryset.count()})
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Error en el servicio'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def persona_lista_direcciones(request):
    """
    Retorna la lista de direcciones asociados al id de la persona.
    :param request:
    :return:
    """
    direcciones = Direccion.objects.filter(persona__id=request.query_params['persona_id']).all()
    return Response({'data': DireccionSerializer(direcciones, many=True).data,
                     'status': status.HTTP_200_OK,
                     'message': None})