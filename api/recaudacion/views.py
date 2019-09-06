import json
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.db.models.aggregates import Count, Sum
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.organico.serializers import UAASerializer
from api.recaudacion.serializers import *
from api.recaudacion.serializers import PuntoEmisionUAAFuncionarioSerializer, OrdenPagoDetalleConCabeceraSerializer
from api.tributacion.serializers import ComprobanteDatosPrincipalesSerializer, ComprobanteImpuestoSerializer, \
    ComprobanteDetalleSerializer
from app.core.models import CatalogoItem, Persona, Direccion
from app.core.utils.general import api_paginacion
from app.recaudacion.models import *
from app.recaudacion.models import PuntoEmisionUAA, OrdenPagoDocumentoDetalle, OrdenPagoDetalle, Producto
from app.recaudacion.templatetags.tags import get_detalle_subtotal, \
    get_formato_secuencial_orden_pago_detalle, get_punto_emision_total, get_total_documentos, get_puntos_emision_total, \
    get_forma_pago_total
from app.recaudacion.views import get_factura_individual_all
from app.reporte.utils.pdf import html_a_pdf
from app.seguridad.utils.permissions import IsPermission
from app.talento_humano.models import Funcionario
from app.tributacion.models import Comprobante, ComprobanteDetalle, ComprobanteImpuesto
from siaa.settings.base import STATIC_ROOT
from app.reporte.utils.excel import generar_excel


class ProductoViewSet(viewsets.ViewSet):
    """
    API para las operaciones CRUD de productos
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(IsPermission('recaudacion.view_producto'))
    @list_route()
    def get_productos_por_paginacion(self, request):
        """
        Retorna un diccionario con la lista de productos, estado de la petición y mensaje.
        Los filtra segun NÚMERO DE ITEMS y NÚMERO DE PÁGINA
        :param request:
        :return:
        """
        try:
            filter = request.query_params['filter']
            page = request.query_params['page']
            numero_items_por_pagina = request.query_params['numberItems']

            if filter:
                queryset = Producto.buscar(filter)
            else:
                queryset = Producto.objects.all()
            productos = api_paginacion(queryset, page, numero_items_por_pagina)
            serializer = ProductoSerializer(productos, many=True)

            return Response({'status': status.HTTP_200_OK,
                             'data': serializer.data,
                             'message': '',
                             'count': queryset.count()})
        except Exception as e:
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': 'Error en el servicio'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(IsPermission('recaudacion.view_producto'))
    def list(self, request):
        """
        Retorna un diccionario con la lista de productos, estado de la petición y mensaje.
        :param request:
        :return:
        """
        try:
            productos = Producto.objects.all()
            serializer = ProductoSerializer(productos, many=True)
            return Response({'status': status.HTTP_200_OK,
                             'data': serializer.data,
                             'message': 'Respuesta con éxito'})
        except Exception as e:
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': 'Error en el servicio'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(IsPermission('recaudacion.view_producto'))
    def retrieve(self, request, pk=None):
        """
        Retorna un diccionario con los datos asociados al producto y su lista
        de uaa asignadas, el estado de la petición y un mensaje.
        :param request:
        :param pk:
        :return:
        """
        try:
            objeto = Producto.objects.get(id=pk)
            producto = ProductoSerializer(objeto).data
            producto['uaas'] = UAASerializer(objeto.uaas.all(), many=True).data
            return Response({'data': producto,
                             'status': status.HTTP_200_OK,
                             'message': None})

        except Producto.DoesNotExist:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': None
                             })

    @method_decorator(IsPermission('recaudacion.delete_producto'))
    def destroy(self, request, pk=None):
        """
        Elimina el producto y retorna un diccionario con información de datos,
        estado de la petición y mensaje
        :param request:
        :param pk:
        :return:
        """
        producto = Producto.objects.get(id=pk)
        try:
            producto.delete()
            return Response({'data': pk,
                             'status': status.HTTP_200_OK,
                             'message': "El producto {0} fue eliminado".format(producto.descripcion.upper())
                             })
        except ProtectedError:
            msg = "El producto {0} asociado a Ordenes de Pago, no puede eliminarce".format(producto.descripcion.upper())
            return HttpResponse(json.dumps({'data': pk,
                                            'status': status.HTTP_400_BAD_REQUEST,
                                            'message': msg}),
                                content_type='application/json')

    @method_decorator(IsPermission('recaudacion.add_producto'))
    def create(self, request):
        """
        Crea un objeto Producto y retorna información del producto creado,
        estado de la petición y mensaje
        :param request:
        :return:
        """
        try:
            producto = Producto()
            producto.tipo_factura_id = request.data['tipo_factura'] if 'tipo_factura' in request.data else None
            producto.tipo_unidad_id = request.data['tipo_unidad'] if 'tipo_unidad' in request.data else None
            producto.tipo_impuesto_id = request.data['tipo_impuesto'] if 'tipo_impuesto' in request.data else None
            serializer = ProductoSerializer(producto, data=request.data)
            if serializer.is_valid():
                serializer.save()
                producto_message = 'Item creado'
                producto_status = status.HTTP_200_OK
            else:
                producto_message = serializer.errors
                producto_status = status.HTTP_400_BAD_REQUEST

            return Response({'data': serializer.data,
                             'status': producto_status,
                             'message': producto_message})

        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': e})

    @method_decorator(IsPermission('recaudacion.change_producto'))
    def update(self, request, pk=None):
        """
        Actualiza el objeto Producto, y retorna información del
        producto actualizado, estado de la petición y mensaje
        :param request:
        :param pk:
        :return:
        """
        try:
            producto = Producto.objects.get(id=pk)
            producto.tipo_factura_id = request.data['tipo_factura'] if 'tipo_factura' in request.data else None
            producto.tipo_unidad_id = request.data['tipo_unidad'] if 'tipo_unidad' in request.data else None
            producto.tipo_impuesto_id = request.data['tipo_impuesto'] if 'tipo_impuesto' in request.data else None
            serializer = ProductoSerializer(producto, data=request.data)
            if serializer.is_valid():
                serializer.save()
                producto_message = 'Item actualizado'
                producto_status = status.HTTP_200_OK
            else:
                producto_message = serializer.errors
                producto_status = status.HTTP_400_BAD_REQUEST

            return Response({'data': serializer.data,
                             'status': producto_status,
                             'message': producto_message})
        except ObjectDoesNotExist as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': e})

    @method_decorator(IsPermission('recaudacion.change_producto'))
    @detail_route(methods=['post'])
    def asignar_uaas_in_producto(self, request, pk=None):
        """
        Asiga una/varias Unidad Academica Administratica (UAA) al producto
        a un producto.
        :param request:
        :return:
        """
        try:
            producto = Producto.objects.get(id=request.data['id_producto'])
            uaas = UAA.objects.filter(id__in=request.data['ids_uaa']).all()
            for uaa in uaas:
                producto.uaas.add(uaa)
            return Response({'data': UAASerializer(uaas, many=True).data,
                             'status': status.HTTP_200_OK,
                             'message': 'UAAs asigando al producto'})

        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': e})

    @method_decorator(IsPermission('recaudacion.change_producto'))
    @detail_route(methods=['post'])
    def delete_uaa_in_producto(self, request, pk=None):
        """
        Elimina una Unidad Academica Administratica (UAA)
        asignada a un producto.
        :param request:
        :return:
        """
        try:
            producto = Producto.objects.get(id=request.data['id_producto'])
            uaa = UAA.objects.get(id=request.data['id_uaa'])
            producto.uaas.remove(uaa)
            return Response({'data': None,
                             'status': status.HTTP_200_OK,
                             'message': 'UAA eiminada del producto'})

        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': e})

    @method_decorator(IsPermission('recaudacion.view_producto'))
    @list_route()
    def get_productos_in_funcionario_in_uaa(self, request):
        """
        Retorna la lista de productos que pertenecen a la Unidad
        Academica Administrativa del funcionario en sesión
        :param requests:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                asignacionDePuesto = funcionario.get_asignacion_puesto_vigente()
                if asignacionDePuesto:
                    productos = Producto.objects.filter(uaas__in=[asignacionDePuesto.uaa_puesto.uaa],
                                                        activo=True).all()
                    return Response({'data': ProductoSerializer(productos, many=True).data,
                                     'status': status.HTTP_200_OK,
                                     'message': None})
                else:
                    message = 'El Funcionario no tiene un puesto de trabajo en estado activo'
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})


class PuntoEmisionViewSet(viewsets.ViewSet):
    """
    API para las operaciones CRUD de Puntos de Emisión
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(IsPermission('recaudacion.view_puntoemision'))
    def list(self, request):
        """
        Retorna un diccionario con la lista de puntos de emision,
        estado de la petición y mensaje
        :param request:
        :return:
        """
        queryset = PuntoEmision.objects.all()
        serializer = PuntoEmisionSerializer(queryset, many=True)
        return Response({'data': serializer.data,
                         'status': status.HTTP_200_OK,
                         'message': None
                         })

    @method_decorator(IsPermission('recaudacion.view_puntoemision'))
    def retrieve(self, request, pk=None):
        """
        Retorna un diccionario con los datos asociados al
        punto de emision el estado de la petición y un mensaje.
        :param request:
        :param pk:
        :return:
        """
        try:
            punto_emision = PuntoEmision.objects.get(id=pk)
            punto_emision_ser = PuntoEmisionSerializer(punto_emision).data
            punto_emision_uaa = PuntoEmisionUAA.objects.filter(punto_emision=punto_emision)
            punto_emision_uaa_ser = PuntoEmisionUAAFuncionarioSerializer(punto_emision_uaa, many=True).data
            return Response({'data': {'punto_emision': punto_emision_ser,
                                      'punto_emision_uaa': punto_emision_uaa_ser},
                             'status': status.HTTP_200_OK,
                             'message': None})

        except PuntoEmision.DoesNotExist:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': None})

    @method_decorator(IsPermission('recaudacion.add_puntoemision'))
    def create(self, request):
        """
        Crea un objeto Punto de Emision y retorna información del punto de emision creado,
        estado de la petición y mensaje
         :param request:
         :return:
         """
        try:
            puntos_emision = PuntoEmision.objects.filter(codigo_establecimiento=request.data['codigo_establecimiento'],
                                                         codigo_facturero=request.data['codigo_facturero']).all()
            if puntos_emision:
                return Response({'data': None,
                                 'status': status.HTTP_400_BAD_REQUEST,
                                 'message': 'Existe un Punto de Emisión con igual código de ESTABLECIMIENTO Y FACTURERO (%s-%s)'
                                            % (
                                                request.data['codigo_establecimiento'],
                                                request.data['codigo_facturero'])})
            else:
                punto_emision = PuntoEmision()
                punto_emision.nro_secuencial = request.data['nro_desde']
                serializer = PuntoEmisionSerializer(punto_emision, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    punto_emision_message = 'Item creado'
                    punto_emision_status = status.HTTP_200_OK
                else:
                    punto_emision_message = serializer.errors
                    punto_emision_status = status.HTTP_400_BAD_REQUEST

                return Response({'data': serializer.data,
                                 'status': punto_emision_status,
                                 'message': punto_emision_message})
        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': e})

    @method_decorator(IsPermission('recaudacion.change_puntoemision'))
    def update(self, request, pk=None):
        """
        Actualiza el objeto Punto de Emision, y retorna información del
        punto de emision actualizado, estado de la petición y mensaje
        :param request:
        :param pk:
        :return:
        """
        try:

            puntos_emision = PuntoEmision.objects.filter(~Q(id=request.data['id']),
                                                         codigo_establecimiento=request.data['codigo_establecimiento'],
                                                         codigo_facturero=request.data['codigo_facturero']).all()
            if puntos_emision:
                return Response({'data': None,
                                 'status': status.HTTP_400_BAD_REQUEST,
                                 'message': 'Existe un Punto de Emisión con igual código de ESTABLECIMIENTO Y FACTURERO (%s-%s)'
                                            % (
                                                request.data['codigo_establecimiento'],
                                                request.data['codigo_facturero'])})
            else:
                punto_emision = PuntoEmision.objects.get(id=pk)
                serializer = PuntoEmisionSerializer(punto_emision, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    punto_emision_message = 'Item actualizado'
                    punto_emision_status = status.HTTP_200_OK
                else:
                    punto_emision_message = serializer.errors
                    punto_emision_status = status.HTTP_400_BAD_REQUEST

                return Response({'data': serializer.data,
                                 'status': punto_emision_status,
                                 'message': punto_emision_message})
        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': e})

    @method_decorator(IsPermission('recaudacion.delete_puntoemision'))
    def destroy(self, request, pk=None):
        """
        Elimina el punto de emision y retorna un diccionario
        con información de datos, estado de la petición
        y mensaje
        :param request:
        :param pk:
        :return:
        """
        punto_emision = PuntoEmision.objects.get(id=pk)
        try:
            punto_emision.delete()
            return Response({'data': None,
                             'status': status.HTTP_200_OK,
                             'message': "Punto de Emisión {0} eliminado".format(punto_emision.descripcion.upper())
                             })
        except ProtectedError:
            return HttpResponse(
                json.dumps(
                    {'data': None,
                     'status': status.HTTP_400_BAD_REQUEST,
                     'message': "El Punto de Emisión {0} asociado a Ordenes de Pago, no puede eliminarce".format(
                         punto_emision.descripcion.upper())}
                ), content_type='application/json')

    @method_decorator(IsPermission('recaudacion.change_puntoemision'))
    @detail_route(methods=['post'])
    def guardar_funcionario_in_punto_emision(self, request, pk=None):

        """
        Asigan un Funcionario a un punto de Emision
        :param request:
        :return:
        """
        try:
            restriccion_codigo = PuntoEmisionUAA.objects.filter(Q(punto_emision_id=request.data['punto_emision']),
                                                                Q(codigo=request.data['codigo']),
                                                                ~Q(id=pk)).all()
            restriccion_funcionario = PuntoEmisionUAA.objects.filter(Q(punto_emision_id=request.data['punto_emision']),
                                                                     Q(funcionario_id=request.data['funcionario']),
                                                                     ~Q(id=pk)).all()

            if restriccion_codigo:
                return Response({'data': None,
                                 'status': status.HTTP_400_BAD_REQUEST,
                                 'message': 'Existe ya un Punto de Emisión UAA con el código %s' % (
                                     request.data['codigo'])
                                 })
            elif restriccion_funcionario:
                return Response({'data': None,
                                 'status': status.HTTP_400_BAD_REQUEST,
                                 'message': 'Existe ya un Punto de Emisión UAA con el funcionario seleccionado'
                                 })
            else:

                if int(pk) != 0:
                    punto_emision_uaa = PuntoEmisionUAA.objects.get(id=pk)
                else:
                    punto_emision_uaa = PuntoEmisionUAA()

                punto_emision_uaa.punto_emision_id = request.data['punto_emision']
                punto_emision_uaa.funcionario_id = request.data['funcionario']
                serializer = PuntoEmisionUAAFuncionarioSerializer(punto_emision_uaa, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    punto_emision_uaa_message = 'Funcionario guardado al punto de emision'
                    punto_emision_uaa_status = status.HTTP_200_OK
                else:
                    punto_emision_uaa_message = serializer.errors
                    punto_emision_uaa_status = status.HTTP_400_BAD_REQUEST

                return Response({'data': serializer.data,
                                 'status': punto_emision_uaa_status,
                                 'message': punto_emision_uaa_message})
        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': str(e)})

    @method_decorator(IsPermission('recaudacion.change_puntoemision'))
    @detail_route(methods=['delete'])
    def eliminar_funcionario_in_punto_emision(self, request, pk=None):

        """
        Elimina una Punto de Emision (UAA)
        :param request:
        :return:
        """
        punto_emision_uaa = PuntoEmisionUAA.objects.get(id=pk)
        try:
            punto_emision_uaa.delete()
            return Response({'data': None,
                             'status': status.HTTP_200_OK,
                             'message': "PUNTO DE EMISIÓN UAA {0} eliminado".format(punto_emision_uaa.codigo.upper())})
        except ProtectedError:
            return HttpResponse(
                json.dumps(
                    {'data': None,
                     'status': status.HTTP_400_BAD_REQUEST,
                     'message': "PUNTO DE EMISIÓN UAA {0} asociado a Ordenes de Pago, no puede eliminarce".format(
                         punto_emision_uaa.codigo.upper())}
                ), content_type='application/json')

    @method_decorator(IsPermission('recaudacion.view_puntoemision'))
    @list_route()
    def get_puntos_emision_activo(self, request):
        """
        Retorna la lista de puntos de emisión en estado activo
        :param requests:
        :return:
        """
        queryset = PuntoEmision.objects.filter(activo=True).all()
        serializer = PuntoEmisionSerializer(queryset, many=True)
        return Response({'data': serializer.data,
                         'status': status.HTTP_200_OK,
                         'message': None
                         })

    @method_decorator(IsPermission('recaudacion.view_puntoemision'))
    @list_route()
    def get_puntos_emision_in_funcionario(self, request):
        """
        Retorna la lista de puntos de emisión al que pertenece
        el funcionario en sesión
        :param requests:
        :return:
        """
        puntos_emision = []
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                puntos_emision_uaa = PuntoEmisionUAA.objects.filter(funcionario=funcionario,
                                                                    punto_emision__activo=True).all().order_by(
                    'punto_emision__codigo_establecimiento', 'punto_emision__codigo_facturero', 'codigo')
                if puntos_emision_uaa:

                    for punto_emision_uaa in puntos_emision_uaa:
                        puntos_emision.append(PuntoEmisionSerializer(punto_emision_uaa.punto_emision).data)

                    return Response({'data': puntos_emision,
                                     'status': status.HTTP_200_OK,
                                     'message': 'Puntos de Emisión'})
                else:
                    message = 'El Funcionario no esta asignado a ningún Punto de Emisión en estado activo'
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'
        return Response({'data': puntos_emision,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('recaudacion.view_puntoemisionuaa'))
    @list_route()
    def get_puntos_emision_uaa_in_funcionario(self, request):
        """
        Retorna la lista de puntos de emisión UAA al que pertenece
        el funcionario en sesión
        :param requests:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                puntos_emision_uaa = PuntoEmisionUAA.objects.filter(funcionario=funcionario,
                                                                    punto_emision__activo=True).all().order_by(
                    'punto_emision__codigo_establecimiento', 'punto_emision__codigo_facturero', 'codigo')
                if puntos_emision_uaa:
                    puntos_emision_uaa_serializer = PuntoEmisionUAAFuncionarioSerializer(puntos_emision_uaa,
                                                                                         many=True).data
                    for punto_emision_uaa in puntos_emision_uaa_serializer:
                        punto_emision_uaa['punto_emision'] = PuntoEmisionSerializer(
                            PuntoEmision.objects.get(id=punto_emision_uaa['punto_emision'])).data

                    return Response({'data': puntos_emision_uaa_serializer,
                                     'status': status.HTTP_200_OK,
                                     'message': 'Puntos de Emisión Unidad Académicia Administrativa (UAA)'})
                else:
                    message = 'El Funcionario no esta asignado a ningún Punto de Emisión UAA en estado activo'
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': [],
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})


class OrdenPagoViewSet(viewsets.ViewSet):
    """
    API para las operaciones CRUD de Ordenes de Pago
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(IsPermission('recaudacion.view_ordenpago'))
    @list_route()
    def get_ordenes_pago_por_paginacion(self, request):
        """
        Retorna las ordenes de pago que estan asociadas al punto de emision uaa y asociada al
        funcionario en sesión. Los filtra segun NÚMERO DE ITEMS y NÚMERO DE PÁGINA
        :param request:
        :return:
        """
        filter = request.GET.get('filter')
        page = request.GET.get('page')
        numero_items_por_pagina = request.GET.get('numberItems')
        punto_emision_uaa_id = request.GET.get('punto_emision_uaa_id', None)

        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario and funcionario.activo:
            # Busca por punto de emisión uaa
            if punto_emision_uaa_id:
                punto_emision_uaa = PuntoEmisionUAA.objects.get(id=punto_emision_uaa_id, funcionario=funcionario)
            # Busca las que no tienen asignado punto de emisión uaa
            else:
                punto_emision_uaa = PuntoEmisionUAA.objects.filter(funcionario=funcionario).first()

            if punto_emision_uaa:
                if filter:
                    queryset = OrdenPago.buscar_por_punto_emision_uaa(
                        filter, punto_emision_uaa if punto_emision_uaa_id else None)
                else:
                    queryset = OrdenPago.objects.filter(
                        punto_emision_uaa=punto_emision_uaa if punto_emision_uaa_id else None
                    ).order_by('-fecha_emision', '-id')

                ordenes_pago = api_paginacion(queryset, page, numero_items_por_pagina)
                serializer = OrdenPagoConDetallesSerializer(ordenes_pago, many=True)

                return Response({'data': serializer.data,
                                 'status': status.HTTP_200_OK,
                                 'count': queryset.count(),
                                 'message': None})
            else:
                message = 'El Funcionario no esta asignado a ningún Punto de Emisión UAA'
        else:
            message = 'El usuario no tiene rol de Funcionario o no esta activo'

        return Response({'data': [],
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('recaudacion.view_ordenpago'))
    def retrieve(self, request, pk=None):
        """
        Retorna un diccionario con los datos asociados a la
         orden de pago, el estado de la petición y un mensaje.
        :param request:
        :param pk:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                if int(pk) != 0:
                    objeto = OrdenPago.objects.get(id=pk)
                    orden_pago = OrdenPagoConDetallesSerializer(objeto).data
                else:
                    punto_emision_uaa_id = request.query_params['punto_emision_uaa_id']
                    punto_emision_uaa = PuntoEmisionUAA.objects.get(id=punto_emision_uaa_id, funcionario=funcionario)
                    orden_pago_obj = OrdenPago()
                    orden_pago_obj.fecha_emision = datetime.now()
                    orden_pago_obj.punto_emision_uaa = punto_emision_uaa
                    orden_pago = OrdenPagoConDetallesSerializer(orden_pago_obj).data

                return Response({'data': orden_pago,
                                 'status': status.HTTP_200_OK,
                                 'message': None})
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('recaudacion.add_ordenpago'))
    def create(self, request):
        """
        Crea una Orden de Pago y retorna información de la Orden de
        Pago creado, estado de la petición y mensaje
        :param request:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario and funcionario.activo:
            try:
                if len(request.data['ordenes_pago_detalle']) > 0:
                    # Registro persona
                    if 'id' in request.data['persona'] and request.data['persona']['id'] is not None:
                        personaobject = Persona.objects.get(id=request.data['persona']['id'])
                    else:
                        personaobject = Persona()
                    personaobject.tipo_documento_id = request.data['persona']['tipo_documento']
                    personaobject.sexo_id = request.data['persona']['sexo']
                    personaserializer = PersonaSerializer(personaobject, data=request.data['persona'])

                    # Guardo la persona
                    if personaserializer.is_valid():
                        persona = personaserializer.save()

                        # Registro de Dirección
                        if 'id' in request.data['direccion'] and request.data['direccion']['id'] is not None:
                            direccionobject = Direccion.objects.get(id=request.data['direccion']['id'])
                        else:
                            direccionobject = Direccion()
                            direccionobject.tipo_direccion = CatalogoItem.get_catalogo_item('TIPO_DIRECCION', 2)
                            request.data['direccion']['persona'] = persona.id
                        direccionserializer = DireccionSerializer(direccionobject, data=request.data['direccion'])

                        # Guardo la direccion
                        if direccionserializer.is_valid():
                            direccion = direccionserializer.save()

                            # Creo la orden de Pago
                            request.data.update({"fecha_emision": datetime.now(), 'estado': OrdenPago.ESTADO_EMITIDA})
                            orden_pago = OrdenPago()
                            orden_pago.persona = persona
                            orden_pago.direccion = direccion
                            serializer_orden_pago = OrdenPagoConDetallesSerializer(orden_pago, data=request.data)

                            # Creo el pago
                            request.data['pago'].update({"fecha_pago": datetime.now()})
                            serializer_pago = PagoSerializer(data=request.data['pago'])

                            if serializer_orden_pago.is_valid():
                                if serializer_pago.is_valid():
                                    # Guardo la orden de pago
                                    serializer_orden_pago.save()
                                    # Guardo los items
                                    punto_emision_uaa = PuntoEmisionUAA.objects.get(
                                        id=request.data['punto_emision_uaa'])
                                    for item in request.data['ordenes_pago_detalle']:
                                        orden_pago_detalle = OrdenPagoDetalle()
                                        orden_pago_detalle.orden_pago = orden_pago
                                        orden_pago_detalle.producto_id = item['producto']['id']
                                        orden_pago_detalle.tipo_impuesto_id = item['tipo_impuesto']['id']
                                        item.update(
                                            {'secuencial': punto_emision_uaa.new_secuencial_orden_pago_detalle(),
                                             'estado': OrdenPago.ESTADO_EMITIDA})
                                        serializer = OrdenPagoDetalleProductoSerializer(orden_pago_detalle, data=item)
                                        if serializer.is_valid():
                                            serializer.save()
                                            punto_emision_uaa.actualizar_secuencial()
                                    # Guardo el pago
                                    pago = serializer_pago.save()
                                    orden_pago.pago = pago
                                    orden_pago.save()

                                    return Response({'data': OrdenPagoConDetallesSerializer(orden_pago).data,
                                                     'status': status.HTTP_200_OK,
                                                     'message': 'Item creado'})
                                else:
                                    message = serializer_pago.errors
                            else:
                                message = serializer_orden_pago.errors
                        else:
                            message = direccionserializer.errors
                    else:
                        message = personaserializer.errors
                else:
                    message = 'No exiten items a guardar'

            except Exception as e:
                message = e
        else:
            message = 'El usuario no tiene rol de Funcionario o no esta activo'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': str(message)})

    @method_decorator(IsPermission('recaudacion.change_ordenpago'))
    @detail_route(methods=['put'])
    def anular(self, request, pk=None):
        """
        Actualiza la Orden de Pago en estado de anulada junto con sus items solo si no son facturados
        :param request:
        :param pk:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario and funcionario.activo:
            orden_pago = get_object_or_404(OrdenPago, id=pk,  estado=OrdenPago.ESTADO_EMITIDA)
            items_facturados = OrdenPagoDocumentoDetalle.objects.filter(
                Q(orden_pago_detalle__orden_pago=orden_pago) &
                Q(comprobante_detalle__comprobante__estado=Comprobante.ESTADO_EMITIDA)).count()

            if items_facturados == 0:
                orden_pago.estado = orden_pago.ESTADO_ANULADA
                orden_pago.ordenes_pago_detalle.update(estado=orden_pago.ESTADO_ANULADA)
                orden_pago.save()
                if orden_pago.pago:
                    orden_pago.fecha_reverso = datetime.now()
                    orden_pago.save()

                return Response({'data': OrdenPagoConDetallesSerializer(orden_pago).data,
                                 'status': status.HTTP_200_OK,
                                 'message': 'Orden de pago anulada'})
            else:
                message = 'No se puede anular por que la Orden de Pago ya ha sido facturada'
        else:
            message = 'El usuario no tiene rol de Funcionario o no esta activo'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('tributacion.view_comprobante'))
    @list_route()
    def get_facturas_emitir_por_ordenes_pago(self, request):
        """
        Retorna la lista de facturas que no han sido emitidas
        de acuerdo a las ordenes de pago, estado de la petición
        y un mensaje.
        :param request:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                desde = request.query_params['desde']
                hasta = request.query_params['hasta']
                punto_emision = PuntoEmision.objects.get(id=request.query_params['punto_emision_id'])

                secuencial = punto_emision.nro_secuencial
                documentos_a_emitir = []

                # Se genera las facturas por dia de emisión de las ordenes de pago
                fecha_dia = datetime.strptime(desde, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(hasta, '%Y-%m-%d').date()

                while fecha_dia <= fecha_fin:
                    documentos_a_emitir_ind, secuencial = get_factura_individual_all(fecha_dia,
                                                                                     punto_emision.id,
                                                                                     secuencial)
                    documentos_a_emitir.extend(documentos_a_emitir_ind)
                    fecha_dia = fecha_dia + timedelta(days=1)

                # Control, verifico que el total de las facturas no sobrepasen el valor de las ordenes de pago no emitidas
                range_desde = datetime.strptime(desde, '%Y-%m-%d')
                range_hasta = datetime.strptime(hasta, '%Y-%m-%d')
                range_hasta += timedelta(seconds=86399)

                ids_emitidas = OrdenPagoDocumentoDetalle.objects.filter(
                    Q(orden_pago_detalle__orden_pago__punto_emision_uaa__punto_emision=punto_emision) &
                    Q(orden_pago_detalle__orden_pago__pago__fecha_pago__range=(range_desde, range_hasta)) &
                    Q(comprobante_detalle__comprobante__estado=OrdenPago.ESTADO_EMITIDA)
                ).values_list('orden_pago_detalle__id', flat=True).distinct().all()

                total_no_emitida = OrdenPagoDetalle.objects.filter(
                    orden_pago__punto_emision_uaa__punto_emision=punto_emision,
                    orden_pago__pago__fecha_pago__range=(range_desde, range_hasta),
                    producto__facturable=True,
                    estado=OrdenPago.ESTADO_EMITIDA).exclude(id__in=ids_emitidas).aggregate(total=Sum('total'))

                total_detalles_no_emitidas = 0 if total_no_emitida['total'] is None else float(
                    total_no_emitida['total'])
                total_documentos = 0
                for documento in documentos_a_emitir:
                    total_documentos += float(documento['total'])

                if round(total_documentos, 2) <= round(total_detalles_no_emitidas, 2):
                    if (secuencial - 1) > int(punto_emision.nro_hasta):
                        msg = 'El último número de documento generado ({0}) para las facturas sobrepasa el máximo configurado ({1}) por el Punto de Emisión'.format(
                            secuencial - 1, punto_emision.nro_hasta)
                    else:
                        msg = None

                    return Response({'data': documentos_a_emitir,
                                     'status': status.HTTP_200_OK,
                                     'message': msg})
                else:
                    message = 'El total de facturas sobrepasa el total de las ordenes de pago, contactese con soporte técnico'
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('tributacion.add_comprobante'))
    @detail_route(methods=['post'])
    def guardar_facturas_por_ordenes_pago(self, request, pk=None):
        """
        Guarda las facturas generadas de acuerdo a las ordenes
        de pago emitidas y a un rango de fechas.
        :param request:
        :param pk:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                try:
                    documentos_a_emitir = request.data['documentos_a_emitir']
                    punto_emision = PuntoEmision.objects.get(id=request.data['punto_emision'])
                    for item in documentos_a_emitir:
                        # Guardado del documento
                        documento = Comprobante()
                        documento.tipo_documento_id = item['tipo_documento']['id']
                        documento.persona_id = item['persona']['id']
                        documento.direccion_id = item['direccion']['id']
                        documento_serializer = ComprobanteDatosPrincipalesSerializer(documento, data=item)
                        if documento_serializer.is_valid():
                            documento = documento_serializer.save()
                            punto_emision.actualizar_secuencial()
                            # Guardado del detalle del documento
                            for subitem in item['documento_detalles']:
                                documento_detalle = ComprobanteDetalle.objects.create(
                                    codigo=subitem['codigo'],
                                    detalle=subitem['detalle'],
                                    detalle_adicional=subitem['detalle_adicional'],
                                    cantidad=subitem['cantidad'],
                                    precio=subitem['precio'],
                                    subtotal=subitem['subtotal'],
                                    impuesto=subitem['impuesto'],
                                    tipo_impuesto_id=subitem['tipo_impuesto']['id'],
                                    tarifa_impuesto=subitem['tipo_impuesto']['valor'],
                                    codigo_impuesto=subitem['tipo_impuesto']['codigo'],
                                    total=subitem['total'],
                                    producto_id=subitem['producto'],
                                    comprobante=documento)
                                # Guardado del detalle del documento orden pago
                                for id_detalle in subitem['orden_pago_detalle_ids']:
                                    OrdenPagoDocumentoDetalle.objects.create(
                                        orden_pago_detalle_id=id_detalle,
                                        comprobante_detalle=documento_detalle)
                            # Guardo el detalle de impuestos
                            for impuesto in item['documento_impuestos']:
                                ComprobanteImpuesto.objects.create(subtotal=impuesto['subtotal'],
                                                                   impuesto=impuesto['impuesto'],
                                                                   tipo_impuesto_id=impuesto['tipo_impuesto']['id'],
                                                                   tarifa_impuesto=impuesto['tipo_impuesto']['valor'],
                                                                   codigo_impuesto=impuesto['tipo_impuesto']['codigo'],
                                                                   comprobante=documento)
                        else:
                            return Response({'data': None,
                                             'status': status.HTTP_400_BAD_REQUEST,
                                             'message': str(documento_serializer.errors)})

                    return Response({'data': None,
                                     'status': status.HTTP_200_OK,
                                     'message': 'Las Facturas fueron guardadas exitosamente'})
                except Exception as e:
                    message = e
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @list_route()
    def get_orden_pago_detalles(self, request):
        """
        Retorna una un diccionario con una lista de las orden de pago detalle y configuración de la impresión.
        Api que se utiliza en el cliente de php (WebClientPrint) para la impresora matricial
        :param request:
        :param pk:
        :return:
        """
        try:
            import locale

            config_impresora = 'default'
            ordenes_pago_detalles = []
            locale.setlocale(locale.LC_TIME, "es_EC.UTF-8")

            funcionario = Funcionario.objects.filter(usuario=request.user).first()
            if funcionario:
                ids = request.query_params['ids'].split('-')
                for id in ids:
                    orden_pago_detalle = OrdenPagoDetalle.objects.get(id=id)
                    orden_pago_detalle_serializer = OrdenPagoDetalleSerializer(orden_pago_detalle).data
                    orden_pago_detalle_serializer['cantidad'] = '%.0f' % orden_pago_detalle.cantidad
                    orden_pago_detalle_serializer['precio'] = '%.2f' % orden_pago_detalle.precio
                    orden_pago_detalle_serializer['impuesto'] = '%.2f' % orden_pago_detalle.impuesto
                    orden_pago_detalle_serializer['fecha_actual'] = str(datetime.now().strftime("%A, %d de %B de %Y"))
                    orden_pago_detalle_serializer[
                        'fecha_emision'] = orden_pago_detalle.orden_pago.fecha_emision.strftime("%Y-%m-%d")
                    orden_pago_detalle_serializer['area'] = orden_pago_detalle.orden_pago.punto_emision_uaa.codigo
                    orden_pago_detalle_serializer['secuencial'] = orden_pago_detalle.get_formato_secuencial()
                    orden_pago_detalle_serializer['cliente_id'] = orden_pago_detalle.orden_pago.persona.numero_documento
                    orden_pago_detalle_serializer[
                        'cliente_nombre'] = orden_pago_detalle.orden_pago.persona.get_nombres_completos().upper()
                    orden_pago_detalle_serializer['usuario_id'] = request.user.persona.numero_documento
                    orden_pago_detalle_serializer['usuario_nombre'] = request.user.persona.get_nombres_completos()
                    config_impresora = orden_pago_detalle.orden_pago.punto_emision_uaa.impresora
                    ordenes_pago_detalles.append(orden_pago_detalle_serializer)

                return Response({'data': {'ordenesPagoDetalles': ordenes_pago_detalles,
                                          'configImpresora': config_impresora},
                                 'status': status.HTTP_200_OK,
                                 'message': None})
            else:
                return Response({'data': None,
                                 'status': status.HTTP_400_BAD_REQUEST,
                                 'message': 'El usuario no tiene rol de Funcionario'})
        except Exception as e:
            return Response({'data': None,
                             'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'message': 'Error en el servidor'})

    @method_decorator(IsPermission('tributacion.view_comprobante'))
    @list_route()
    def get_facturas_emitidas_por_ordenes_pago(self, request):
        """
        Retorna la lista de Comprobantes que han sido guardadas de acuerdo a las ordenes de pago y
        en estan en estado de EMITIDA, estado de la petición y un mensaje.
        :param request:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                comprobantes_serializer = []
                fecha_desde = datetime.strptime(request.query_params['desde'], '%Y-%m-%d')
                fecha_hasta = datetime.strptime(request.query_params['hasta'], '%Y-%m-%d')
                fecha_hasta += timedelta(seconds=86399)

                comprobantes = Comprobante.objects.filter(
                    fecha_emision__range=(fecha_desde, fecha_hasta),
                    estado=Comprobante.ESTADO_EMITIDA).order_by('fecha_emision', 'numero_documento')

                for comprobante in comprobantes:
                    comprobante_serializer = ComprobanteDatosPrincipalesSerializer(comprobante).data
                    comprobante_serializer['documento_detalles'] = ComprobanteDetalleSerializer(
                        comprobante.comprobante_detalles, many=True).data
                    comprobante_serializer['documento_impuestos'] = ComprobanteImpuestoSerializer(
                        comprobante.comprobante_impuestos, many=True).data
                    comprobantes_serializer.append(comprobante_serializer)

                return Response({'data': comprobantes_serializer,
                                 'status': status.HTTP_200_OK,
                                 'message': None})
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('tributacion.change_comprobante'))
    @detail_route(methods=['post'])
    def anular_facturas_emitidas_por_ordenes_pago(self, request, pk=None):
        """
        Anula las facturas que fueron generadas de acuerdo a las ordenes
        de pago.
        :param request:
        :param pk:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if funcionario:
            if funcionario.activo:
                try:
                    message = ''
                    comprobantes_anular = request.data
                    for item in comprobantes_anular:
                        comprobante = Comprobante.objects.get(id=item['id'])
                        if comprobante.estado == Comprobante.ESTADO_EMITIDA:
                            comprobante.estado = Comprobante.ESTADO_ANULADO
                            comprobante.save()
                            message += comprobante.numero_documento + " "

                    return Response({'data': None,
                                     'status': status.HTTP_200_OK,
                                     'message': 'Las facturas han sido anuladas ' + message})
                except Exception as e:
                    message = e
            else:
                message = 'El Funcionario no esta en estado activo'
        else:
            message = 'El usuario no tiene rol de Funcionario'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': message})

    @method_decorator(IsPermission('recaudacion.change_ordenpago'))
    @detail_route(methods=['put'])
    def validar(self, request, pk=None):
        """
        Actualiza la Orden de Pago de PENDIENTE a EMITIDA creando un registro de PAGO
        :param request:
        :param pk:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        punto_emision_uaa = PuntoEmisionUAA.objects.filter(funcionario=funcionario).first()
        if punto_emision_uaa:
            orden_pago = OrdenPago.objects.get(id=pk)
            if orden_pago.pago is None and orden_pago.estado==orden_pago.ESTADO_PENDIENTE:
                if orden_pago.fecha_vencimiento is None or orden_pago.fecha_vencimiento and orden_pago.fecha_vencimiento >= datetime.now():
                    request.data.update({"fecha_pago": datetime.now()})
                    serializer_pago = PagoSerializer(data=request.data)
                    if serializer_pago.is_valid():
                        pago = serializer_pago.save()
                        orden_pago.pago = pago
                        orden_pago.punto_emision_uaa = punto_emision_uaa
                        orden_pago.estado = orden_pago.ESTADO_EMITIDA
                        for item in orden_pago.ordenes_pago_detalle.all():
                            item.secuencial = punto_emision_uaa.new_secuencial_orden_pago_detalle()
                            item.estado = orden_pago.ESTADO_EMITIDA
                            item.save()
                            punto_emision_uaa.actualizar_secuencial()
                        orden_pago.save()

                        return Response({'data': OrdenPagoConDetallesSerializer(orden_pago).data,
                                         'status': status.HTTP_200_OK,
                                         'message': 'Orden de pago emitida'})
                    else:
                        message = serializer_pago.errors
                else:
                    message = 'Registro con fecha de vencimiento caducado %s' % (orden_pago.fecha_vencimiento)
            else:
                message = 'La orden de pago ya tiene una registro de Pago o ya se encuentra emitida'
        else:
            message = 'El funcionario no esta asignado a ningún punto de emisión'

        return Response({'data': None,
                         'status': status.HTTP_400_BAD_REQUEST,
                         'message': str(message)})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def comprobante_reporte_detalle(request):
    """
    Genera reporte para visualizar el detalle de una factura
    que fue generada de las ordenes de pago de un cliente
    :param request:
    return:
    """
    try:
        context = {
            'title': 'Factura',
            'titulo': 'Universidad Nacional de Loja',
            'subtitulo': 'Sistema de Recaudación',
            'asunto': 'Número de documento %s' % (request.data['numero_documento']),
            'detalle': 'Documento generado a partir de las Ordenes de Pago del Usuario',
            'fecha': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            'usuario': request.user,
            'documento': request.data,
        }
        url_template = 'recaudacion/reporte_comprobante.html'
        url_css = STATIC_ROOT + '/css/recaudacion/reporte.css'
        return html_a_pdf(request, url_template, context, url_css, 'detalle-factura.pdf')


    except:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error al generar el Pdf'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def comprobante_reporte_generadas(request):
    """
    Genera reporte consolidado de las facturas que fueron
    generadas de las ordenes de pago en un rango de fechas
    :param request:
    return:
    """
    try:
        context = {
            'size': 'A4 landscape',
            'title': 'Facturas',
            'titulo': 'Universidad Nacional de Loja',
            'subtitulo': 'Sistema de Recaudación',
            'asunto': 'Reporte Consolidado',
            'detalle': 'Documentos generados a partir de las Ordenes de Pago emitidas desde %s hasta %s' % (
                request.data['fecha_desde'], request.data['fecha_hasta']),
            'fecha': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            'usuario': request.user,
            'documentos': request.data['documentos_a_emitir'],
            'facturasGuardadas': False
        }

        url_template = 'recaudacion/reporte_comprobante_consolidado.html'
        url_css = STATIC_ROOT + '/css/recaudacion/reporte.css'
        return html_a_pdf(request, url_template, context, url_css, 'consolidado-facturas.pdf')

    except Exception as e:
        print(e)
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error al generar el Pdf'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def comprobante_reporte_guardadas(request):
    """
    Genera reporte consolidado de las Facturas que fueron guardadas de acuerdo
    al punto de emision
    :param request:
    return:
    """
    try:
        estados = {"P": "Pendiente", "E": "Enviado", "D": "Devuelto", "N": "No autorizado", "A": "Autorizado"}
        fecha_desde = datetime.strptime(request.data['fechaDesde'], '%Y-%m-%d')
        fecha_hasta = datetime.strptime(request.data['fechaHasta'], '%Y-%m-%d')
        fecha_hasta += timedelta(seconds=86399)
        punto_emision_id = request.data['puntoEmision']
        formato = request.data['formato']

        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        documentos_all = []
        if funcionario:

            documentos = OrdenPagoDocumentoDetalle.objects.values('comprobante_detalle__comprobante__id').filter(
                orden_pago_detalle__orden_pago__punto_emision_uaa__punto_emision__id=punto_emision_id,
                comprobante_detalle__comprobante__fecha_emision__range=(fecha_desde, fecha_hasta)
            ).annotate(count=Count('comprobante_detalle__comprobante__id')).order_by(
                'comprobante_detalle__comprobante__fecha_emision', 'comprobante_detalle__comprobante__numero_documento')

            for documento in documentos:
                documento_objeto = Comprobante.objects.get(id=documento['comprobante_detalle__comprobante__id'])
                documento_serializer = ComprobanteDatosPrincipalesSerializer(documento_objeto).data
                documento_serializer['documento_detalles'] = ComprobanteDetalleSerializer(
                    documento_objeto.comprobante_detalles, many=True).data
                documento_serializer['clave_acceso'] = 'Sin registro'
                documento_serializer['estado_fe'] = 'Sin registro'

                for item in Comprobante.objects.raw('SELECT '
                                                    'tributacion_comprobante.id, '
                                                    'tributacion_comprobante.numero_documento, '
                                                    'comprobante_electronico.clave_acceso, '
                                                    'comprobante_electronico.estado '
                                                    'FROM public.tributacion_comprobante, sri_servicios.comprobante_electronico '
                                                    'WHERE tributacion_comprobante.id = comprobante_electronico.comprobante_id '
                                                    'AND tributacion_comprobante.id = %s '
                                                    'ORDER BY comprobante_electronico.fecha_envia',
                                                    [documento_objeto.id]):
                    documento_serializer['clave_acceso'] = '' if item.clave_acceso is None else item.clave_acceso
                    documento_serializer['estado_fe'] = '' if item.estado is None else estados.get(item.estado,
                                                                                                   item.estado)

                documentos_all.append(documento_serializer)

            if formato == 'pdf':
                context = {
                    'size': 'A4 landscape',
                    'title': 'Reporte consolidado',
                    'titulo': 'Universidad Nacional de Loja',
                    'subtitulo': 'Sistema de Recaudación',
                    'asunto': 'Reporte Consolidado',
                    'detalle': 'Documentos guardados desde %s hasta %s' % (fecha_desde, fecha_hasta),
                    'fecha': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'usuario': request.user,
                    'documentos': documentos_all,
                    'facturasGuardadas': True
                }

                url_template = 'recaudacion/reporte_comprobante_consolidado.html'
                url_css = STATIC_ROOT + '/css/recaudacion/reporte.css'
                return html_a_pdf(request, url_template, context, url_css, 'consolidado-facturas-guardadas.pdf')

            else:
                cabeceras = ["Número", "Fecha", "Clave de acceso", "Estado", "Estado Factura Electronica", "Cliente",
                             "Rubro", "Cantidad", "Precio Unit", "Subtotal", "Impuesto", "Valor Imp.", "Total"]

                lista = []
                for documento in documentos_all:
                    lista.extend([(documento['numero_documento'],
                                   datetime.strptime(documento['fecha_emision'],
                                                     "%Y-%m-%dT%H:%M:%S"),
                                   documento['clave_acceso'],
                                   documento['estado'],
                                   documento['estado_fe'],
                                   documento['persona']['nombres_completos'].upper(),
                                   "%s-%s %s" % (
                                       detalle['codigo'], detalle['detalle'], detalle['detalle_adicional']),
                                   detalle['cantidad'],
                                   detalle['precio'],
                                   detalle['subtotal'],
                                   detalle['tipo_impuesto']['nombre'],
                                   detalle['impuesto'],
                                   detalle['total']
                                   ) for detalle in documento['documento_detalles']])

                workbook = generar_excel(filas=lista, cabeceras=cabeceras)

                ws = workbook.get_sheet("Reporte")

                fila = len(lista) + 12
                if len(documentos_all) > 0:
                    total = get_total_documentos(documentos_all)
                    ws.write(fila, 8, "TOTALES")
                    ws.write(fila, 9, total['subtotal'])
                    ws.write(fila, 11, total['impuesto'])
                    ws.write(fila, 12, total['total'])

                    fila += 2
                    ws.write_merge(fila, fila, 4, 5, "TOTAL EMITIDAS")
                    ws.write_merge(fila, fila, 6, 7, "TOTAL ANULADAS")
                    ws.write(fila, 8, "TOTAL")
                    fila += 1
                    ws.write_merge(fila, fila, 4, 5, total['total_emitidas'])
                    ws.write_merge(fila, fila, 6, 7, total['total_anuladas'])
                    ws.write(fila, 8, total['total'])

                # Totales
                response = HttpResponse(content_type='application/ms-excel')
                contenido = "attachment; filename={0}".format("consolidado-ordenes-pago.xlsx")
                response["Content-Disposition"] = contenido
                workbook.save(response)
                return response

        else:
            return Response({'status': status.HTTP_404_NOT_FOUND,
                             'message': 'No existe el funcionario'})
    except Exception as e:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error al generar el archivo'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def orden_pago_reporte_detalle(request):
    """
    Genera reporte para imprimir comprobante de la orden de pago detalle
    :param request:
    return:
    """
    try:
        import locale
        locale.setlocale(locale.LC_TIME, "es_EC.UTF-8")
        orden_pago_detalles = []

        for item in request.data:
            orden_pago_detalles.append(OrdenPagoDetalle.objects.get(id=item['id']))

        context = {
            'fecha': str(datetime.now().strftime("%A, %d de %B de %Y")),
            'usuario': request.user,
            'orden_pago_detalles': orden_pago_detalles,
            'range': range(3)
        }

        url_template = 'recaudacion/reporte_orden_pago_detalle.html'
        url_css = STATIC_ROOT + '/css/recaudacion/reporte.css'
        return html_a_pdf(request, url_template, context, url_css, 'orden-pago-item.pdf')

    except:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error al generar el Pdf'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def orden_pago_reporte_consolidado(request):
    """
    Genera reporte consolidado de las Ordenes de Pago que fueron emitidas en un rango de fechas y para el
    punto de emision UAA al que pertenece el usuario o todos los puntos de emisión UAA si es admin, en pdf o excel.
    Si tiene un registro de pago, busca por fecha de pago, caso contrario por fecha de orden de pago
    :param request:
    return:
    """
    try:
        tipo = request.data['tipo']
        fecha_desde = datetime.strptime(request.data['fechaDesde'], '%Y-%m-%d')
        fecha_hasta = datetime.strptime(request.data['fechaHasta'], '%Y-%m-%d')
        fecha_hasta += timedelta(seconds=86399)
        punto_emision_id = request.data['puntoEmision']
        formato = request.data['formato']
        totales = []

        funcionario = Funcionario.objects.filter(usuario=request.user).first()
        if tipo == 'admin':
            puntos_emision_uaas = PuntoEmisionUAA.objects.filter(punto_emision_id=punto_emision_id).all()
        else:
            puntos_emision_uaas = PuntoEmisionUAA.objects.filter(punto_emision_id=punto_emision_id,
                                                                 funcionario=funcionario).all()

        puntos_emision_uaas_serializer = PuntoEmisionUAAFuncionarioSerializer(puntos_emision_uaas, many=True).data
        for punto_emision_uaa in puntos_emision_uaas_serializer:
            qset = Q(Q(orden_pago__punto_emision_uaa_id=punto_emision_uaa['id']) &
                     ((Q(orden_pago__pago__isnull=False) & Q(orden_pago__pago__fecha_pago__range=[fecha_desde, fecha_hasta])) |
                      (Q(orden_pago__pago__isnull=True) & Q(orden_pago__fecha_emision__range=[fecha_desde, fecha_hasta]))
                      )
                     )

            ordenes_pago_emitidas = OrdenPagoDetalle.objects.filter(qset).filter(
                estado=OrdenPago.ESTADO_EMITIDA).all().order_by('orden_pago__fecha_emision', 'secuencial')

            ordenes_pago_anuladas = OrdenPagoDetalle.objects.filter(qset).filter(
                estado=OrdenPago.ESTADO_ANULADA).all().order_by('orden_pago__fecha_emision', 'secuencial')

            punto_emision_uaa['ordenes_pago_emitidas'] = OrdenPagoDetalleConCabeceraSerializer(ordenes_pago_emitidas,
                                                                                               many=True).data
            punto_emision_uaa['ordenes_pago_anuladas'] = OrdenPagoDetalleConCabeceraSerializer(ordenes_pago_anuladas,
                                                                                               many=True).data

        if formato == 'pdf':
            context = {
                'size': 'A4 landscape',
                'title': 'Reporte consolidado',
                'titulo': 'Universidad Nacional de Loja',
                'subtitulo': 'Sistema de Recaudación',
                'asunto': 'Reporte Consolidado de Ordenes de Pago',
                'detalle': 'Ordenes de Pago emitidas desde %s hasta %s' % (fecha_desde, fecha_hasta),
                'fecha': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'usuario': request.user,
                'puntos_emision_uaas': puntos_emision_uaas_serializer,
                'totales': totales,
                'CHOICE_FORMA_PAGO': Pago.CHOICE_FORMA_PAGO
            }

            url_template = 'recaudacion/reporte_orden_pago_consolidado.html'
            url_css = STATIC_ROOT + '/css/recaudacion/reporte.css'
            return html_a_pdf(request, url_template, context, url_css, 'consolidado-ordenes-pago.pdf')

        else:

            # Encabezado
            cabeceras = ['Punto de emisión', 'Secuencial', 'Fecha', 'Cliente', 'Código', 'Rubro', 'Cantidad',
                         'Precio Unit', 'Subtotal',
                         'Impuesto', 'Valor Imp.', 'Total', 'Estado']

            # Escribimos los datos en las celdas
            lista = []
            for punto_emision_uaa in puntos_emision_uaas_serializer:
                # Punto de Emisión
                get_punto_emision_total(totales, punto_emision_uaa)

                lista.extend([(punto_emision_uaa['descripcion'] + "-" + punto_emision_uaa['codigo'],
                               get_formato_secuencial_orden_pago_detalle(detalle['secuencial']),
                               detalle['fecha_emision'],
                               detalle['nombres_completos'],
                               detalle['producto_codigo'],
                               detalle['producto_descripcion'] + " " + detalle['observacion'],
                               detalle['cantidad'],
                               detalle['precio'],
                               get_detalle_subtotal(detalle),
                               detalle['tipo_impuesto']['nombre'],
                               detalle['impuesto'],
                               detalle['total'],
                               "Emitida") for detalle in punto_emision_uaa['ordenes_pago_emitidas']])

                lista.extend([(punto_emision_uaa['descripcion'] + "-" + punto_emision_uaa['codigo'],
                               get_formato_secuencial_orden_pago_detalle(detalle['secuencial']),
                               detalle['fecha_emision'],
                               detalle['nombres_completos'],
                               detalle['producto_codigo'],
                               detalle['producto_descripcion'] + " " + detalle['observacion'],
                               detalle['cantidad'],
                               detalle['precio'],
                               get_detalle_subtotal(detalle),
                               detalle['tipo_impuesto']['nombre'],
                               detalle['impuesto'],
                               detalle['total'],
                               "Anulada") for detalle in punto_emision_uaa['ordenes_pago_anuladas']])

            # Totales
            workbook = generar_excel(filas=lista, cabeceras=cabeceras)
            ws = workbook.get_sheet("Reporte")
            fila = len(lista) + 12
            if len(totales) > 0:
                # Escribo las cabeceras
                fila += 1
                columna = len(Pago.CHOICE_FORMA_PAGO) + 3
                ws.write_merge(fila, fila, 3, columna, 'Emitidas')
                columna += 1
                ws.write(fila, columna, 'Anuladas')
                fila += 1

                # Escribo las cabeceras de las formas de pago
                ws.write_merge(fila, fila, 0, 2, 'Punto Emisión UAA')
                columna = 3
                for key, value in Pago.CHOICE_FORMA_PAGO:
                    ws.write(fila, columna, value)
                    columna += 1
                ws.write(fila, columna, 'Subtotal')
                fila += 1

                # Escribo los totales de los puntos de emisión
                for total in totales:
                    ws.write_merge(fila, fila, 0, 2, total['punto_emision_uaa'].upper())
                    columna = 3
                    for key, value in Pago.CHOICE_FORMA_PAGO:
                        ws.write(fila, columna, total['total_forma_pago'][key])
                        columna += 1
                    ws.write(fila, columna, total['total_emitidas'])
                    columna += 1
                    ws.write(fila, columna, total['total_anuladas'])
                    fila += 1

                # Escribo los totales generales
                ws.write_merge(fila, fila, 0, 2, 'TOTAL GENERAL')
                columna = 3
                for key, value in Pago.CHOICE_FORMA_PAGO:
                    ws.write(fila, columna, get_forma_pago_total(totales, key))
                    columna += 1
                ws.write(fila, columna, get_puntos_emision_total(totales, 'total_emitidas'))
                columna += 1
                ws.write(fila, columna, get_puntos_emision_total(totales, 'total_anuladas'))

            response = HttpResponse(content_type="application/ms-excel")
            contenido = "attachment; filename={0}".format("consolidado-ordenes-pago.xlsx")
            response["Content-Disposition"] = contenido
            workbook.save(response)
            return response

    except Exception as e:
        return Response({'error': e, 'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error al generar el archivo'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def orden_pago_reporte_productos(request):
    """
    Genera reporte para imprimir consolidado de venta por producto o todos los productos en pdf o excel.
    Si tiene un registro de pago, busca por fecha de pago, caso contrario por fecha de orden de pago
    :param request:
    return:
    """
    try:
        fecha_desde = datetime.strptime(request.data['fechaDesde'], '%Y-%m-%d')
        fecha_hasta = datetime.strptime(request.data['fechaHasta'], '%Y-%m-%d')
        fecha_hasta += timedelta(seconds=86399)
        punto_emision_id = request.data['puntoEmision']
        formato = request.data['formato']
        tipo = request.data['tipo']

        if tipo == 'admin':
            filtro = Q(Q(orden_pago__punto_emision_uaa__punto_emision_id=punto_emision_id) &
                       ((Q(orden_pago__pago__isnull=False) & Q(orden_pago__pago__fecha_pago__range=[fecha_desde, fecha_hasta])) |
                        (Q(orden_pago__pago__isnull=True) & Q(orden_pago__fecha_emision__range=[fecha_desde, fecha_hasta]))
                        )
                       )
        else:
            funcionario = Funcionario.objects.filter(usuario=request.user).first()
            filtro = Q(Q(orden_pago__punto_emision_uaa__punto_emision_id=punto_emision_id) &
                       Q(orden_pago__punto_emision_uaa__funcionario=funcionario) &
                       ((Q(orden_pago__pago__isnull=False) & Q(orden_pago__pago__fecha_pago__range=[fecha_desde, fecha_hasta])) |
                        (Q(orden_pago__pago__isnull=True) & Q(orden_pago__fecha_emision__range=[fecha_desde, fecha_hasta]))
                        )
                       )

        if 'producto' in request.data:
            producto = Producto.objects.get(id=request.data['producto'])
            detalle = 'Ordenes de Pago emitidas desde %s hasta %s del producto %s' % (
                fecha_desde, fecha_hasta, producto.codigo)
            filtro_emitidas = filtro & (Q(estado='EMITIDA') & Q(producto=producto))
            filtro_anuladas = filtro & (Q(estado='ANULADA') & Q(producto=producto))
        else:
            detalle = 'Ordenes de Pago emitidas desde %s hasta %s unificado por código del producto' % (
                fecha_desde, fecha_hasta)
            filtro_emitidas = filtro & Q(estado='EMITIDA')
            filtro_anuladas = filtro & Q(estado='ANULADA')

        detalle_emitidas = OrdenPagoDetalle.objects.values(
            'producto_id', 'producto_codigo', 'producto_descripcion'
        ).filter(filtro_emitidas).annotate(total=Sum('total'), cantidad=Sum('cantidad'))

        detalle_anuladas = OrdenPagoDetalle.objects.values(
            'producto_id', 'producto_codigo', 'producto_descripcion'
        ).filter(filtro_anuladas).annotate(total=Sum('total'), cantidad=Sum('cantidad'))

        if formato == 'pdf':
            context = {
                'size': 'A4',
                'title': 'Reporte consolidado',
                'titulo': 'Universidad Nacional de Loja',
                'subtitulo': 'Sistema de Recaudación',
                'asunto': 'Reporte Consolidado de Ventas por Producto',
                'detalle': detalle,
                'fecha': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'usuario': request.user,
                'detalle_emitidas': detalle_emitidas,
                'detalle_anuladas': detalle_anuladas,
            }

            url_template = 'recaudacion/reporte_orden_pago_productos.html'
            url_css = STATIC_ROOT + '/css/recaudacion/reporte.css'
            return html_a_pdf(request, url_template, context, url_css, 'consolidado-venta-producto.pdf')

        else:

            # Encabezado
            cabeceras = ['Código', 'Descripción', 'Cantidad', 'Total']
            tamanios = [256 * 45, 256 * 70, 256 * 10, 256 * 8]
            # Escribimos los datos en las celdas

            lista = []
            if len(detalle_emitidas) > 0:
                # Titulo emitidas
                lista.extend([['RECAUDACIÓN POR PRODUCTO - EMITIDAS']])

                lista.extend([(detalle['producto_codigo'],
                               detalle['producto_descripcion'],
                               detalle['cantidad'],
                               detalle['total']) for detalle in detalle_emitidas])

            if len(detalle_anuladas) > 0:
                # Titulo anuladas
                lista.extend([[], ['RECAUDACIÓN POR PRODUCTO - ANULADAS']])

                lista.extend([(detalle['producto_codigo'],
                               detalle['producto_descripcion'],
                               detalle['cantidad'],
                               detalle['total']) for detalle in detalle_anuladas])

            workbook = generar_excel(filas=lista, cabeceras=cabeceras, titulo='Reporte', tamanio_columnas=tamanios)

            response = HttpResponse(content_type="application/ms-excel")
            contenido = "attachment; filename={0}".format("consolidado-venta-producto.xlsx")
            response["Content-Disposition"] = contenido
            workbook.save(response)
            return response

    except:
        return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                         'message': 'Error al generar el archivo'})
