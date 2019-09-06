"""
Modulo para gestionar los reportes de la aplicacion
El modelo Plantilla, es utilizado para crear las plantillas de pdfs, aunque se puede generar excel a partir de éstos.
El modelo PlantillaModelo guardar la vista previa de la plantilla.
"""
__version__ = '0.1'
__author__ = 'JJM'

from django.db import models

from app.seguridad.models import AuditModel


class Plantilla(AuditModel):
    codigo = models.CharField(max_length=45, unique=True,
                              error_messages={'unique': "El codigo ya existe en otra plantilla",
                                              'invalid': 'Your email address is incorrect'})
    descripcion = models.CharField(max_length=255)
    definicion = models.TextField()

    class Meta:
        db_table = 'reporte"."plantilla'

    def __str__(self):
        return self.descripcion


class PlantillaModelo(models.Model):

    key = models.CharField(max_length=36)
    definicion = models.TextField()
    data = models.TextField()
    is_test_data = models.BooleanField()
    pdf_file = models.BinaryField(null=True)
    pdf_file_size = models.IntegerField(null=True)
    created_on = models.DateTimeField()

    class Meta:
        db_table = 'reporte"."plantilla_modelo'
