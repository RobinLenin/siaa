from django.db import models
from suds.sudsobject import Object as SudsObject

class PersonaBsg(models.Model):
    CondicionCedulado = models.TextField()
    FechaCedulacion = models.TextField()
    NUI = models.CharField(max_length=20, unique=True)
    Nombre = models.TextField()
    Nacionalidad = models.TextField()
    FechaNacimiento = models.TextField()
    LugarNacimiento = models.TextField()
    Calle = models.TextField()
    NumeroCasa = models.CharField(max_length=20)
    Domicilio = models.TextField()
    Instruccion = models.TextField(null=True)
    Profesion = models.TextField(null=True)
    EstadoCivil = models.TextField()
    Conyuge = models.TextField(null=True)
    NombreMadre = models.TextField()
    NombrePadre = models.TextField(null=True)
    Sexo = models.CharField(max_length=20)
    Genero = models.CharField(max_length=20, null=True)
    FechaInscripcionGenero = models.TextField(null=True)
    LugarInscripcionGenero = models.TextField(null=True)
    FechaInscripcionDeFuncion = models.TextField(null=True)

    FechaConsulta = models.DateTimeField(auto_now=True)

    def get_object_suds(self):
        objectSuds = SudsObject()
        objectIterable = self.__dict__

        for item in objectIterable:
            if item != '_state':
                setattr(objectSuds, item, objectIterable[item])

        return  objectSuds

    @staticmethod
    def get_defaults(kwars):
        defaults = {}
        defaults['CondicionCedulado'] = kwars.get('CondicionCedulado', '')
        defaults['FechaCedulacion'] = kwars.get('FechaCedulacion', '')
        defaults['NUI'] = kwars.get('NUI', '')
        defaults['Nombre'] = kwars.get('Nombre', '')
        defaults['Nacionalidad'] = kwars.get('Nacionalidad', '')
        defaults['FechaNacimiento'] = kwars.get('FechaNacimiento', '')
        defaults['LugarNacimiento'] = kwars.get('LugarNacimiento', '')
        defaults['Calle'] = kwars.get('Calle', '')
        defaults['NumeroCasa'] = kwars.get('NumeroCasa', '')
        defaults['Domicilio'] = kwars.get('Domicilio', '')
        defaults['Instruccion'] = kwars.get('Instruccion', '')
        defaults['Profesion'] = kwars.get('Profesion', '')
        defaults['EstadoCivil'] = kwars.get('EstadoCivil', '')
        defaults['Conyuge'] = kwars.get('Conyuge', '')
        defaults['NombreMadre'] = kwars.get('NombreMadre', '')
        defaults['NombrePadre'] = kwars.get('NombrePadre', '')
        defaults['Sexo'] = kwars.get('Sexo', '')
        defaults['Genero'] = kwars.get('Genero', '')
        defaults['FechaInscripcionGenero'] = kwars.get('FechaInscripcionGenero', '')
        defaults['LugarInscripcionGenero'] = kwars.get('LugarInscripcionGenero', '')
        defaults['FechaInscripcionDeFuncion'] = kwars.get('FechaInscripcionDefuncion', '')
        return  defaults

    class Meta():
        db_table = 'bsg"."personabsg'



class DiscapacidadBsg(models.Model):
    Nombres = models.TextField(null=True)
    Apellidos = models.TextField(null=True)
    FechaNacimiento = models.DateTimeField(null=True)
    CodigoConadis = models.TextField(null=True)
    FechaConadis = models.DateTimeField(null=True)
    DeficienciaPredomina = models.TextField(null=True)
    GradoDiscapacidad = models.CharField(max_length=20, null=True)
    PorcentajeDiscapacidad = models.CharField(max_length=20)
    Genero = models.CharField(max_length=5, null=True)
    NivelInstruccion = models.TextField(null=True)
    Parroquia = models.TextField(null=True)
    Canton = models.TextField(null=True)
    Provincia = models.TextField(null=True)
    Direccion = models.TextField(null=True)
    DireccionReferencia = models.TextField(null=True)
    TlfCelular = models.TextField(null=True)

    NumeroIdentificacion = models.CharField(max_length=20, unique=True)
    FechaConsulta = models.DateTimeField(auto_now=True)

    def get_object_suds(self):
        objectSuds = SudsObject()
        objectIterable = self.__dict__

        for item in objectIterable:
            if objectIterable[item] is not None and item != '_state':
                setattr(objectSuds, item, objectIterable[item])

        return  objectSuds

    class Meta():
        db_table = 'bsg"."discapacidadbsg'

class TituloBsg(models.Model):
    area = models.TextField(null=True)
    areaCodigo = models.TextField(null=True)
    subarea = models.TextField(null=True)
    subareaCodigo = models.TextField(null=True)
    fechaGrado = models.TextField(null=True)
    fechaRegistro = models.TextField()
    ies = models.TextField()
    nivel = models.TextField()
    nombreClasificacion = models.TextField(null=True)
    nombreDetalleCampo = models.TextField(null=True)
    nombreTitulo = models.TextField()
    nombres = models.TextField()
    numeroIdentificacion = models.CharField(max_length=20)
    numeroRegistro = models.TextField()
    observacion = models.TextField(null=True)
    tipoExtranjeroColegio = models.TextField(null=True)
    tipoNivel = models.TextField(null=True)
    tipoTitulo = models.TextField()

    FechaConsulta = models.DateTimeField(auto_now=True)

    def get_object_suds(self):
        objectSuds = SudsObject()
        objectIterable = self.__dict__

        for item in objectIterable:
            if objectIterable[item] is not None and item != '_state':
                setattr(objectSuds, item, objectIterable[item])

        return  objectSuds

    class Meta():
        db_table = 'bsg"."titulobsg'








