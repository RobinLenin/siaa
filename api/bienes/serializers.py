# Proyecto:siaa
# Autor   : Yazber Romero
# Fecha   :08/06/16 15:21
from rest_framework import serializers

from api.core.serializers import CatalogoItemSerializer
from api.core.serializers import PersonaSerializer
from api.curricular.serializers import CarreraSerializer
from app.bienes.models import *


class DetallesPrestacionSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(read_only=True)
    carrera = CarreraSerializer(read_only=True)
    tipo_prestacion = serializers.SerializerMethodField('get_prestacion_tipo')
    codigo_prestacion = serializers.SerializerMethodField('get_prestacion_codigo')
    estado = CatalogoItemSerializer(read_only=True)
    razon = CatalogoItemSerializer(read_only=True)
    funcion = CatalogoItemSerializer(read_only=True)
    tipo_ente = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = DetallePrestacion
        fields = (
            'id', 'numero', 'fecha_registro', 'fecha_finalizacion', 'hora_entrada', 'hora_salida', 'tipo_prestacion',
            'codigo_prestacion', 'persona', 'carrera', 'razon', 'estado', 'funcion', 'tipo_ente', 'activo')

    def get_prestacion_tipo(self, obj):
        return obj.get_prestacion_tipo()

    def get_prestacion_codigo(self, obj):
        return obj.get_prestacion_codigo()


class PrestacionSerializer(serializers.ModelSerializer):
    detalles = DetallesPrestacionSerializer(many=True, read_only=True)
    tipo = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = Prestacion
        fields = ('codigo', 'fecha_registro', 'tipo', 'detalles')
