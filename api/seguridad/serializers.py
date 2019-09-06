from rest_framework import serializers

from api.core.serializers import PersonaSerializer
from app.seguridad.models import *


class UsuarioPersonaSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase usuario con sus datos principales y de persona
    """
    persona = PersonaSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ('id', 'nombre_de_usuario', 'correo_electronico_institucional', 'foto_url', 'persona')
