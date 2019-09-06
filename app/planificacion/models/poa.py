from datetime import datetime
from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app.seguridad.models import AuditModel
from .pedi import MetaAnual


class Actividad(AuditModel):
    ESTADO_EJECUCION = "Ejecucion"
    ESTADO_FINALIZADO = "Finalizado"
    ESTADO_PLANIFICADO = "Planificado"
    #ESTADO_ATRASADO = "Atrasado"
    #ESTADO_NO = "No"
    ESTADOS = (
        (ESTADO_PLANIFICADO, 'Planificado'),
        (ESTADO_EJECUCION, 'En ejecucion'),
        (ESTADO_FINALIZADO, 'Finalizado'),
    #    (ESTADO_ATRASADO, 'Atrasado'),
    #    (ESTADO_NO, 'No Realizado'),
    )

    inicio = models.DateField(verbose_name='Fecha inicio')
    fin = models.DateField(verbose_name='Fecha fin')
    indicador = models.CharField(max_length=250)
    meta_especifica = models.CharField(max_length=250)
    nombre = models.CharField(max_length=250)
    codigo = models.CharField(max_length=25)
    peso = models.PositiveSmallIntegerField(default=0, blank=True,
                                            verbose_name="Peso en la meta")  # un porcentaje de peso de la actividad
    # peso_fijo si Falso, peso se calcula por division simple de total de actividades de meta
    peso_fijo = models.BooleanField(default=False)
    progreso = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    meta_anual = models.ForeignKey(MetaAnual, related_name='actividades', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Acción / Actividad"
        verbose_name_plural = "Acciones / Actividades"
        ordering = ['meta_anual', 'codigo', 'nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if getattr(self, '_progreso_changed', True):
            print("progreso change")
        super(Actividad, self).save(*args, **kwargs)

    def get_estado(self):
        """
        Retorna el estado de la actividad en terminos de fechas
        :return: ESTADO
        """
        hoy = datetime.now().date()
        if self.inicio < hoy < self.fin:
            return self.ESTADO_EJECUCION
        elif hoy < self.inicio:
            return self.ESTADO_PLANIFICADO
        else:
            return self.ESTADO_FINALIZADO

    def get_porcentaje_disponible(self):
        return self.meta_anual.get_porcentaje_disponible(self)

    def actualizar_progreso(self):
        if self.verificaciones.filter(actividad_termino=True).count():
            self.progreso = 100
        else:
            total = self.progreso = self.verificaciones.count()
            self.progreso = total * 100 / (total + 1)
        self.save()


class Verificacion(AuditModel):
    '''
    Modelo para los medios de verificacion de cada actividad
    '''
    nombre = models.CharField(max_length=250)
    documento = models.FileField(upload_to='planificacion/')
    actividad_termino = models.BooleanField(default=False)
    actividad = models.ForeignKey(Actividad, related_name='verificaciones', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Medio de Verificación"
        verbose_name_plural = "Medios de Verificación"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super(Verificacion, self).save(*args, **kwargs)
        self.actividad.actualizar_progreso()

    def delete(self, *args, **kwargs):
        res = super(Verificacion, self).delete(*args, **kwargs)
        self.actividad.actualizar_progreso()
        return res


@receiver(post_delete, sender=Verificacion)
def submission_delete(sender, instance, **kwargs):
    """
    Eliminar el archivo(del servidor) cargado como medio de verificacion, luego de eliminado el objeto en la BD
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    instance.documento.delete(False)


class Presupuesto(models.Model):
    '''
    presupuesto que requiere cada Actividad
    '''
    PUBLICO = 'PUBLICO'
    AUTOGESTION = 'AUTOGESTION'
    OTROS = 'OTROS'
    TIPO_SEL = (
        (PUBLICO, 'Fondos Publicos'),
        (AUTOGESTION, 'Autogestión'),
        (OTROS, 'Otros'),
    )

    CORRIENTE = 'CORRIENTE'
    INVERSION = 'INVERSION'
    DESTINO_SEL = (
        (CORRIENTE, 'Gasto Corriente'),
        (INVERSION, 'Inversion'),
    )
    tipo = models.CharField(
        max_length=15,
        choices=TIPO_SEL,
        default=PUBLICO,
    )
    destino = models.CharField(
        max_length=15,
        choices=DESTINO_SEL,
        default=CORRIENTE,
    )
    valor = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    actividad = models.OneToOneField(Actividad, null=True, on_delete=models.SET_NULL, related_name='presupuesto')
