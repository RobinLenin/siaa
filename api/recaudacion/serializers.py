from rest_framework import serializers

from api.configuracion.serializers import DetalleParametrizacionSerializer
from api.core.serializers import CatalogoItemSerializer, DireccionSerializer
from api.core.serializers import PersonaSerializer
from api.talento_humano.serializers import  FuncionarioPersonaSerializer
from app.recaudacion.models import Producto, PuntoEmision, PuntoEmisionUAA, OrdenPago, OrdenPagoDetalle, Pago


class PagoSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Pago
    """
    class Meta:
        model = Pago
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Producto
    """
    tipo_impuesto = DetalleParametrizacionSerializer(read_only=True)
    tipo_factura = CatalogoItemSerializer(read_only=True)
    tipo_unidad = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = Producto
        exclude = ('uaas',)


class PuntoEmisionSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Puntos de Emision
    """

    class Meta:
        model = PuntoEmision
        fields = '__all__'


class PuntoEmisionUAAFuncionarioSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Puntos de Emision UAA con el funcionario asignado
    """
    funcionario = FuncionarioPersonaSerializer(read_only=True)


    class Meta:
        model = PuntoEmisionUAA
        fields = '__all__'


class OrdenPagoDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Orden Pago Detalle
    """
    tipo_impuesto = DetalleParametrizacionSerializer(read_only=True)

    class Meta:
        model = OrdenPagoDetalle
        fields = '__all__'

class OrdenPagoDetalleProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Orden Pago Detalle con el producto asociado
    """
    producto = ProductoSerializer(read_only=True)
    tipo_impuesto = DetalleParametrizacionSerializer(read_only=True)

    class Meta:
        model = OrdenPagoDetalle
        exclude = ('orden_pago',)

class OrdenPagoDetalleConCabeceraSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Orden Pago Detalle con los datos principales de la orden de Pago
    """
    producto = ProductoSerializer(read_only=True)
    tipo_impuesto = DetalleParametrizacionSerializer(read_only=True)
    nombres_completos = serializers.SerializerMethodField()
    fecha_emision = serializers.SerializerMethodField()

    class Meta:
        model = OrdenPagoDetalle
        fields = '__all__'

    def get_nombres_completos(self, obj):
        return obj.orden_pago.persona.get_nombres_completos()

    def get_fecha_emision(self, obj):
        return obj.orden_pago.pago.fecha_pago if obj.orden_pago.pago else obj.orden_pago.fecha_emision


class OrdenPagoConDetallesSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase Orden de Pago con todos sus datos asociados incluidos los items
    """
    persona = PersonaSerializer(read_only=True)
    estado_orden = CatalogoItemSerializer(read_only=True)
    direccion = DireccionSerializer(read_only=True)
    ordenes_pago_detalle = OrdenPagoDetalleProductoSerializer(many=True, read_only=True)
    pago = PagoSerializer(read_only=True)

    class Meta:
        model = OrdenPago
        fields = '__all__'

