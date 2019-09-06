from rest_framework import serializers

from api.core.serializers import CatalogoItemSerializer
from app.curricular.models import Carrera

class CarreraSerializer(serializers.ModelSerializer):
    tipo_carrera = CatalogoItemSerializer(read_only=True)
    nivel_formacion = CatalogoItemSerializer(read_only=True)
    modalidad_estudios = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = Carrera
        fields = '__all__'
