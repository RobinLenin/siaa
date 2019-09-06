# -*- encoding: utf-8 -*-
from django.db import models


class Carrera(models.Model):
    ies = models.ForeignKey('core.IES', on_delete=models.PROTECT)
    codigo_senescyt = models.CharField(max_length=6, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    siglas = models.CharField(max_length=20, blank=True, null=True)
    nivel_formacion = models.ForeignKey('core.CatalogoItem', related_name='nivel_formacion',
                                        limit_choices_to={'catalogo__codigo': 'NIVEL_FORMACION'}
                                        , on_delete=models.PROTECT)
    modalidad_estudios = models.ForeignKey('core.CatalogoItem', related_name='modalidad_estudios',
                                           limit_choices_to={'catalogo__codigo': 'MODALIDAD_ESTUDIO'}
                                           , on_delete=models.PROTECT)
    fecha_creacion = models.DateField(blank=True, null=True)
    fecha_aprobacion = models.DateField(blank=True, null=True)
    numero_aprobacion = models.CharField(max_length=50, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    vigente = models.BooleanField(default=False)

    class Meta:
        ordering = ['nombre', ]

    def __str__(self):
        return '%s(%s)' % (self.nombre, self.modalidad_estudios.nombre)
