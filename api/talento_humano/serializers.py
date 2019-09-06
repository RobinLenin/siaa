from rest_framework import serializers

from app.talento_humano.models import *


class FuncionarioPersonaSerializer(serializers.ModelSerializer):
    """
    Serializador para la clase funcionario junto con datos principales de la persona
    """

    class Meta:
        model = Funcionario
        fields = ('id', 'usuario', 'get_foto_url', 'get_nombres', 'get_apellidos')
