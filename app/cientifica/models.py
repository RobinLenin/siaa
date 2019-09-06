from django.db import models

class ProduccionCientifica(models.Model):
    expediente = models.OneToOneField('core.Expediente', on_delete=models.CASCADE)


class ArticuloRevista(models.Model):
    produccion_cientifica = models.ForeignKey('ProduccionCientifica', on_delete=models.CASCADE)
    codigo_institucional = models.CharField(max_length=150, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    issn = models.CharField(max_length=140)
    base_datos_indexada = models.ForeignKey('core.CatalogoItem', blank=True, null=True,
                                               related_name='base_datos_indexada',
                                               limit_choices_to={'catalogo__codigo': 'BASE_DATOS_INDEXADA'}, on_delete=models.SET_NULL)
    nombre_revista = models.CharField(max_length=255)
    fecha_publicacion = models.DateField()
    campo_detallado = models.ForeignKey('academico.CampoDetallado', on_delete=models.PROTECT)
    aceptado = models.BooleanField(default=False)
    publicado = models.BooleanField(default=False)
    filiacion = models.BooleanField(default=False)
    observacion = models.TextField(blank=True, null=True)
    url = models.TextField(default=None, blank=True, null=True)

class Ponencia(models.Model):
    produccion_cientifica = models.ForeignKey('ProduccionCientifica', on_delete=models.CASCADE)
    codigo_institucional = models.CharField(max_length=150, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    nombre_evento = models.CharField(max_length=255)
    fecha_publicacion = models.DateField()
    pais = models.ForeignKey('core.Pais', on_delete=models.PROTECT)
    ciudad = models.CharField(max_length=255)
    campo_detallado = models.ForeignKey('academico.CampoDetallado', on_delete=models.PROTECT)
    filiacion = models.BooleanField(default=False)
    observacion = models.TextField(blank=True, null=True)
    url = models.TextField(default=None, blank=True, null=True)

class Libro(models.Model):
    produccion_cientifica = models.ForeignKey('ProduccionCientifica', on_delete=models.CASCADE)
    codigo_institucional = models.CharField(max_length=150, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    isbn = models.CharField(max_length=140)
    fecha_publicacion = models.DateField()
    revisado_pares = models.BooleanField(default=False)
    filiacion = models.BooleanField(default=False)
    campo_detallado = models.ForeignKey('academico.CampoDetallado', on_delete=models.PROTECT)
    observacion = models.TextField(blank=True, null=True)
    url = models.TextField(default=None, blank=True, null=True)

class CapituloLibro(models.Model):
    produccion_cientifica = models.ForeignKey('ProduccionCientifica', on_delete=models.CASCADE)
    codigo_institucional = models.CharField(max_length=150, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    nombre_libro = models.CharField(max_length=255)
    isbn = models.CharField(max_length=140)
    editor = models.CharField(max_length=255)
    fecha_publicacion = models.DateField()
    campo_detallado = models.ForeignKey('academico.CampoDetallado', on_delete=models.PROTECT)
    observacion = models.TextField(blank=True, null=True)
    url = models.TextField(default=None, blank=True, null=True)