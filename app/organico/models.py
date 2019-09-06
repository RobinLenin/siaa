# -*- encoding: utf-8 -*-
from django.db import models

from app.core.models import CatalogoItem


class EstructuraOrganizacional(models.Model):
    ies = models.ForeignKey('core.IES', on_delete=models.PROTECT)
    tipo_estructura_organica = models.ForeignKey('core.CatalogoItem',
                                                 related_name='tipo_estructura_organica',
                                                 limit_choices_to={'catalogo__codigo': 'TIPO_ESTRUCTURA_ORGANICA'}, on_delete=models.PROTECT)
    vigente = models.BooleanField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Estructuras organizacionales'

    def __str__(self):
        return str(self.fecha_inicio)


class UAA(models.Model):
    estructura_organizacional = models.ForeignKey(EstructuraOrganizacional, on_delete=models.CASCADE)
    estructura_organica = models.ForeignKey('core.CatalogoItem',
                                            related_name='estructura_organica',
                                            limit_choices_to={'catalogo__codigo': 'ESTRUCTURA_ORGANICA'}
                                            , on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    siglas = models.CharField(max_length=50, null=True, blank=True)
    campus = models.ForeignKey('core.Campus', on_delete=models.CASCADE)
    academico = models.BooleanField(default=True)
    administrativo = models.BooleanField(default=True)
    uaa = models.ForeignKey('self', null=True, related_name="serie", blank=True, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    extension = models.CharField(max_length=20, blank=True, null=True)
    localizacion = models.OneToOneField('edificios.Localizacion', null=True, blank=True, on_delete=models.SET_NULL)
    tipo_uaa = models.ForeignKey('core.CatalogoItem',
                                 blank=True,
                                 null=True,
                                 related_name='tipo_uaa',
                                 limit_choices_to={'catalogo__codigo': 'TIPO_UAA'},
                                 on_delete=models.SET_NULL)
    correo = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Unidades Académicas administrativas'
        verbose_name = 'Unidad Académico Administrativo'
        ordering = ['nombre']

    def __str__(self):
        padre = self.get_uaa_padre_tipo()
        if padre:
            return str(self.nombre) + ' - ' + str(padre)
        return str(self.nombre)

    def get_uaa_padre_tipo(self):
        """
        Devuelve la primera uaa que tenga un tipo_uaa que la reconoce como la uaa Padre
        :return:
        """
        if self.uaa:
            if self.uaa.tipo_uaa:
                return self.uaa
            else:
                return self.uaa.get_uaa_padre_tipo()

    def get_uaa_hijas(self, nombre_tipo_uaa=None, tipo_uaa=None):
        """
        Devuelve todas las UAA hijas que cumple una caracteristica de tipo de UAA
        :param nombre_tipo_uaa:
        :param tipo_uaa:
        :return: Arreglo de uaa
        """
        if tipo_uaa is None:
            if nombre_tipo_uaa is None:
                return None
            tipo_uaa = CatalogoItem.get_catalogo_item_nombre('TIPO_UAA', nombre_tipo_uaa)
        uass = []
        for uaa_hija in self.serie.all():
            if uaa_hija.tipo_uaa == tipo_uaa:
                uass.append(uaa_hija)
            uass = uass + uaa_hija.get_uaa_hijas(tipo_uaa=tipo_uaa)
        return uass

    def get_uaa_hijas_todas(self):
        """
        Devuelve todas las uaa hijas
        :return: 
        """
        uass = []
        for uaa_hija in self.serie.all():
            uass.append(uaa_hija)
            uass = uass + uaa_hija.get_uaa_hijas_todas()
        return uass
