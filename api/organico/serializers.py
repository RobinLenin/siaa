from rest_framework import serializers

from api.core.serializers import CatalogoItemSerializer
from app.organico.models import UAA


class UAASerializer(serializers.ModelSerializer):
    tipo_uaa = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = UAA
        fields = '__all__'
