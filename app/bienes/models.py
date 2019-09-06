from django.db import models
from django.db.models import Q

from app.core.models import CatalogoItem, Persona
from app.curricular.models import Carrera
from app.organico.models import UAA
from app.seguridad.models import Usuario
from app.talento_humano.models import Funcionario


class Prestacion(models.Model):
    codigo = models.CharField(max_length=255)
    fecha_registro = models.DateField()
    usuario = models.ForeignKey('seguridad.Usuario', null=True, on_delete=models.SET_NULL)
    tipo = models.ForeignKey('core.CatalogoItem',
                             null=True,
                             related_name='tipo_prestacion',
                             limit_choices_to={'catalogo__codigo': 'TIPO_PRESTACION'}, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = 'Prestaciones'


class DetallePrestacion(models.Model):
    numero = models.PositiveSmallIntegerField(blank=True, null=True)
    fecha_registro = models.DateField()
    fecha_finalizacion = models.DateField(blank=True, null=True)
    hora_entrada = models.TimeField(blank=True)
    hora_salida = models.TimeField(blank=True, null=True)
    tipo_ente = models.ForeignKey('core.CatalogoItem',
                                  null=True,
                                  related_name='tipo_ente',
                                  limit_choices_to={'catalogo__codigo': 'TIPO_ENTE'}, on_delete=models.SET_NULL)
    razon = models.ForeignKey('core.CatalogoItem',
                              null=True,
                              related_name='razon_prestacion',
                              limit_choices_to={'catalogo__codigo': 'RAZON_PRESTACION'}, on_delete=models.SET_NULL)
    funcion = models.ForeignKey('core.CatalogoItem',
                                null=True,
                                related_name='funcion_prestacion',
                                limit_choices_to={'catalogo__codigo': 'FUNCION_PRESTACION'}, on_delete=models.SET_NULL)
    estado = models.ForeignKey('core.CatalogoItem',
                               null=True,
                               related_name='estado_prestacion',
                               limit_choices_to={'catalogo__codigo': 'ESTADO_PRESTACION'}, on_delete=models.SET_NULL)
    persona = models.ForeignKey('core.Persona', related_name='persona', null=True, on_delete=models.SET_NULL)
    carrera = models.ForeignKey('curricular.Carrera', related_name='carrera', blank=True, null=True, on_delete=models.SET_NULL)
    prestacion = models.ForeignKey(Prestacion, related_name='detalles', on_delete=models.CASCADE)
    activo = models.NullBooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Detalle Prestaciones'
        ordering = ['estado__id', '-fecha_registro']

    def get_prestacion_tipo(self):
        """
        Retorna el tipo de prestación
        :return:
        """
        return self.prestacion.tipo.nombre

    def get_prestacion_codigo(self):
        """
        Retorna el codigo de la prestacion
        :return:
        """
        return self.prestacion.codigo

    @staticmethod
    def buscar(criterio):
        """
        Buscar registros por criterios
        :param criterio:
        :return:
        """
        p_criterio = criterio.split(" ")
        qset = Q()
        for i in p_criterio:
            qset = qset & (
                    Q(persona__primer_apellido__icontains=i) | Q(persona__segundo_apellido__icontains=i) |
                    Q(persona__primer_nombre__icontains=i) | Q(persona__segundo_nombre__icontains=i) |
                    Q(persona__numero_documento__icontains=i) | Q(fecha_registro__icontains=i) |
                    Q(estado__nombre__icontains=i))
        return DetallePrestacion.objects.filter(qset).distinct()
