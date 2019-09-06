from django.db import models

class OfertaAcademica(models.Model):
    ESTADO_ACTIVO = "ACTIVO"
    ESTADO_CERRADO = "CERRADO"
    ESTADO_INACTIVO = "INACTIVO"
    CHOICE_ESTADO = ((ESTADO_ACTIVO, "Activo"),
                     (ESTADO_CERRADO, "Cerrado"),
                     (ESTADO_INACTIVO, "Inactivo"),)

    estado = models.CharField(max_length=25, choices=CHOICE_ESTADO, default=ESTADO_INACTIVO)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    nombre = models.TextField()

    periodo_academico = models.ForeignKey('PeriodoAcademico', on_delete=models.CASCADE,
                                          related_name='ofertas_academicas')
    class Meta:
        verbose_name = 'Oferta académica'
        verbose_name_plural = 'Ofertas académicas'

    def __str__(self):
        return self.nombre


class OfertaPensum(models.Model):
    oferta_academica = models.ForeignKey('OfertaAcademica', on_delete=models.CASCADE, related_name='ofertas_pensum')
    pensum = models.ForeignKey('Pensum', on_delete=models.PROTECT, related_name='ofertas_pensum')


    class Meta:
        permissions = (('add_ofertaasignaturanivel', 'Puede ofertar asignaturas'),)
        verbose_name = 'Oferta de pensum'
        verbose_name_plural = 'Ofertas de pensum'


class OfertaAsignaturaNivel(models.Model):
    asignatura_nivel = models.ForeignKey('AsignaturaNivel', on_delete=models.PROTECT, related_name='ofertas_asignatura_nivel')
    oferta_pensum = models.ForeignKey('OfertaPensum', on_delete=models.CASCADE, related_name='ofertas_asignatura_nivel')

    class Meta:
        verbose_name = 'Oferta de asignatura nivel'
        verbose_name_plural = 'Ofertas de asignatura nivel'


class PeriodoAcademico(models.Model):
    asistencia_minima_aprobar = models.PositiveSmallIntegerField() # En porcentaje (%)
    nombre = models.TextField()
    nota_minima_aprobar = models.PositiveSmallIntegerField()

    periodo_lectivo = models.ForeignKey('core.CatalogoItem',
                                       limit_choices_to={'catalogo__codigo': 'PERIODO_ACADEMICO_PERIODO_LECTIVO'},
                                       on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Período académico'
        verbose_name_plural = 'Períodos académicos'
        ordering = ['periodo_lectivo__nombre', 'nombre']

    def __str__(self):
        return self.nombre


class PeriodoMatricula(models.Model):
    TIPO_ORDINARIA = "ORDINARIA"
    TIPO_EXTRAORDINARIA = "EXTRAORDINARIA"
    TIPO_ESPECIAL = "ESPECIAL"
    CHOICE_TIPO = ((TIPO_ORDINARIA, "Ordinaria"),
                   (TIPO_EXTRAORDINARIA, "Extraordinaria"),
                   (TIPO_ESPECIAL, "Especial"),)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_ORDINARIA)

    oferta_academica = models.ForeignKey('OfertaAcademica', on_delete=models.CASCADE, related_name='periodos_matricula')

    class Meta:
        unique_together = ('tipo', 'oferta_academica')
        verbose_name = 'Período de matrícula'
        verbose_name_plural = 'Períodos de matrícula'
