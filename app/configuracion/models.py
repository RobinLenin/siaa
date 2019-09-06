from django.db import models

from app.core.models import CatalogoItem


class Parametrizacion(models.Model):
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(null=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(null=True, blank=True)
    activo = models.NullBooleanField(default=True)
    grupo = models.ForeignKey('core.CatalogoItem',
                              null=True,
                              related_name='grupo_parametrizacion',
                              limit_choices_to={'catalogo__codigo': 'GRUPO_PARAMETIZACION'}, on_delete=models.SET_NULL)
    class Meta:
        verbose_name_plural = 'Parametrizaciones'

class DetalleParametrizacion(models.Model):
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=250)
    valor = models.CharField(max_length=250)
    parametrizacion = models.ForeignKey(Parametrizacion, related_name='detalles', on_delete=models.CASCADE)

    @staticmethod
    def get_detalle_parametrizacion(codigo_parametrizacion, codigo_detalle_parametrizacion):
        """
        Obtiene un detalle parametrización de acuerdo a su codigo  y al codigo de la parametrización padre
        :param codigo_parametrizacion:
        :param codigo_detalle_parametrizacion:
        :return:
        """
        return DetalleParametrizacion.objects.filter(parametrizacion__codigo=codigo_parametrizacion,
                                                     codigo=codigo_detalle_parametrizacion).first()


class Planificacion(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(null=True)
    fecha_desde = models.DateField(null=True)
    fecha_hasta = models.DateField(null=True)
    activo = models.NullBooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Planificaciones'

    def __str__(self):
        return self.nombre

    def get_numero_dias(self):
        """
        Obtiene los dias de diferencia entre las fecha de inicio y fin de la planificación
        :return:
        """
        diferencia = self.fecha_hasta - self.fecha_desde
        return diferencia.days + 1


class DetallePlanificacion(models.Model):
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(null=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    activo = models.NullBooleanField(default=True)
    planificacion = models.ForeignKey(Planificacion, related_name="detalles", on_delete=models.CASCADE)

    class Meta:
        ordering = ['fecha_desde', 'nombre']

    def __str__(self):
        return str(self.nombre)

    def get_numero_dias(self):
        """
        Obtiene los dias de diferencia entre las fecha de inicio y fin del detalle planificación
        :return:
        """
        diferencia = self.fecha_hasta - self.fecha_desde
        return diferencia.days + 1
