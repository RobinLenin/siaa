from rest_framework import serializers

from app.configuracion.models import *


class DetalleParametrizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleParametrizacion
        fields = '__all__'
