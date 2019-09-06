from rest_framework import serializers

from api.configuracion.serializers import DetalleParametrizacionSerializer
from api.core.serializers import PersonaSerializer, DireccionSerializer, CatalogoItemSerializer
from app.tributacion.models import ComprobanteDetalle, Comprobante, ComprobanteImpuesto


class ComprobanteImpuestoSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase ComprobanteImpuesto
    """
    tipo_impuesto = DetalleParametrizacionSerializer(read_only=True)

    class Meta:
        model = ComprobanteImpuesto
        fields = '__all__'


class ComprobanteDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase ComprobanteDetalle
    """
    tipo_impuesto = DetalleParametrizacionSerializer(read_only=True)

    class Meta:
        model = ComprobanteDetalle
        fields = '__all__'


class ComprobanteDatosPrincipalesSerializer(serializers.ModelSerializer):
    """
    Serializador de la clase Comprobante con sus datos de persona y dirección
    """
    persona = PersonaSerializer(read_only=True)
    direccion = DireccionSerializer(read_only=True)
    tipo_documento = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = Comprobante
        fields = '__all__'
