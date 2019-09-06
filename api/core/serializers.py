from rest_framework import serializers

from app.core.models import Pais, Provincia, Canton, Parroquia, CatalogoItem, Persona, \
    Direccion


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'


class CantonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canton
        fields = '__all__'


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = '__all__'


class ParroquiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parroquia
        fields = '__all__'


class CatalogoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoItem
        fields= '__all__'


class CatalogoItemRecursivoSerializer(serializers.ModelSerializer):
    padre = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = CatalogoItem
        fields = ('id', 'nombre', 'codigo_th', 'codigo_sg', 'padre', 'orden')


class DireccionSerializer(serializers.ModelSerializer):
    tipo_direccion = CatalogoItemSerializer(read_only=True)

    class Meta:
        model = Direccion
        fields = '__all__'


class PersonaSerializer(serializers.ModelSerializer):
    tipo_documento = CatalogoItemSerializer(read_only=True)
    tipo_discapacidad = CatalogoItemSerializer(read_only=True)
    grado_discapacidad = CatalogoItemSerializer(read_only=True)
    sexo = CatalogoItemSerializer(read_only=True)
    estado_civil = CatalogoItemSerializer(read_only=True)
    tipo_etnia = CatalogoItemSerializer(read_only=True)
    tipo_sangre = CatalogoItemSerializer(read_only=True)
    condicion_cedulado = CatalogoItemSerializer(read_only=True)
    nacionalidad = CatalogoItemSerializer(read_only=True)
    nacionalidad_indigena = CatalogoItemSerializer(read_only=True)

    edad = serializers.SerializerMethodField()
    nombres_completos = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = ('id', 'tipo_documento', 'numero_documento',
                  'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
                  'fecha_nacimiento', 'profesion', 'correo_electronico', 'correo_electronico_alternativo',
                  'numero_libreta_militar', 'anios_residencia',
                  'discapacidad', 'porcentaje_discapacidad', 'fecha_registro_conadis', 'numero_carnet_conadis',
                  'tipo_discapacidad', 'grado_discapacidad',
                  'sexo', 'estado_civil', 'tipo_etnia', 'tipo_sangre', 'condicion_cedulado', 'nacionalidad',
                  'nacionalidad_indigena',
                  'edad', 'nombres_completos', 'foto_url')

    def get_nombres_completos(self, obj):
        return obj.get_nombres_completos()

    def get_foto_url(self, obj):
        return obj.get_foto_url()

    def get_edad(self, obj):
        return obj.get_edad()


class PersonaKohaSerializer(serializers.ModelSerializer):
    nacionalidad = serializers.StringRelatedField()
    sexo = serializers.StringRelatedField()
    estado_civil= serializers.StringRelatedField()
    tipo_documento = serializers.StringRelatedField()
    nombres = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField()

    class Meta:
        model = Persona
        fields = ('tipo_documento', 'numero_documento', 'nombres', 'apellidos',
                  'fecha_nacimiento', 'correo_electronico', 'correo_electronico_alternativo',
                  'sexo', 'estado_civil',  'nacionalidad')

    def get_nombres(self, obj):
        return '{}'.format(obj.get_nombres())

    def get_apellidos(self, obj):
        return '{} {}'.format(obj.get_apellidos())

