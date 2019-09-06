from decimal import Decimal

from django.db import models
from django.db.models import F

from django.core.validators import MinValueValidator

from app.talento_humano.models import Puesto
from app.core.models import PeriodoFiscal


class PlanEstrategico(models.Model):
    """
    Modelo que permite alamacenar los planes estratégicos instuitucionales
    """
    nombre = models.CharField(max_length=250)
    codigo = models.CharField(max_length=25)
    activo = models.BooleanField(default=True)
    periodos = models.ManyToManyField(PeriodoFiscal, related_name='planes_estrategicos')
    # nuevo =  models.BooleanField(default=False)


    class Meta:
        verbose_name = "Plan Estratégico Institucional"
        verbose_name_plural = "Planes Estratégicos Institucionales"
        ordering = ['activo','-nombre']

    def __str__(self):
        return self.nombre


class Politica(models.Model):
    '''
    Modelo para las politicas de un Objetivo, Un  Objetivo tiene varias politicas,
    '''
    nombre = models.CharField(max_length=250)
    plan_estrategico = models.ForeignKey(PlanEstrategico, related_name='politicas', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Políticas"

    def __str__(self):
        return self.nombre

class Estrategia(models.Model):
    '''
    Modelo para las estrategias de un Objetivo, Un  Objetivo tiene varias estrategias,
    '''
    nombre = models.CharField(max_length=250)
    plan_estrategico = models.ForeignKey('PlanEstrategico', related_name='estrategias', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Estrategias"

    def __str__(self):
        return self.nombre


class ObjetivoEstrategico(models.Model):
    '''
    Modelo para los objetivos estrategicos Institucionales del PEDI
    '''
    EJE_DOCENCIA = 'DOCENCIA'
    EJE_INVESTIGACION = 'INVESTIGACION'
    EJE_VINCULACION = 'VINCULACION'
    EJE_ORGANIZACION = 'ORGANIZACION'
    EJES_ESTRATEGICOS = (
        (EJE_DOCENCIA, 'Función Docencia'),
        (EJE_INVESTIGACION, 'Función Investigación'),
        (EJE_VINCULACION, 'Función Vinculación'),
        (EJE_ORGANIZACION, 'Función Organizacion'),
    )

    nombre = models.CharField(max_length=500)
    codigo = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    plan_estrategico = models.ForeignKey(PlanEstrategico, related_name='objetivos_estrategicos',
                                         on_delete=models.CASCADE)
    eje_estrategico = models.CharField(max_length=50, choices=EJES_ESTRATEGICOS, default=EJE_DOCENCIA)


    class Meta:
        verbose_name = "Objetivo Estratégico Institucional"
        verbose_name_plural = "Objetivos Estratégicos Institucionales"
        ordering = ['codigo']

    def __str__(self):
        return self.nombre


class ObjetivoOperativo(models.Model):
    '''
    Modelo para los objetivos operativos Institucionales del PEDI
    '''
    nombre = models.CharField(max_length=500)
    codigo = models.CharField(max_length=25)
    activo = models.BooleanField(default=True)
    indicador = models.CharField(max_length=250, null=True)
    objetivo_estrategico = models.ForeignKey(ObjetivoEstrategico, related_name='objetivos_operativos',
                                             on_delete=models.CASCADE)


    class Meta:
        verbose_name = "Objetivo Operativo Institucional"
        verbose_name_plural = "Objetivos Operativos Institucionales"
        ordering = ['codigo']

    def __str__(self):
        return self.nombre

    def eliminar(self):
        self.activo = False
        self.save()

    def indicadores(self):
        return Indicador.objects.filter(resultado__objetivo_operativo=self)

class Resultado(models.Model):
    '''
    Modelo para los resultados esperados de cada Proyecto/Objetivo operativo
    '''
    nombre = models.CharField(max_length=500)
    codigo = models.CharField(max_length=25)
    objetivo_operativo = models.ForeignKey(ObjetivoOperativo, related_name='resultados', on_delete=models.CASCADE)
    responsables = models.ManyToManyField(Puesto, related_name='resultados', blank=True)

    class Meta:
        verbose_name = "Resultado Esperado"
        verbose_name_plural = "Resultados Esperados"

    def __str__(self):
        return '%s. %s' %(self.codigo, self.nombre)

    def eliminar(self):
        self.delete()

    def responsables_ids(self):
        return self.responsables.values_list('id', flat=True)

class Indicador(models.Model):
    '''
    Indicadores para cada resultado esperado del objetivo operativo
    '''
    nombre = models.CharField(max_length=500)
    resultado = models.ForeignKey(Resultado, related_name='indicadores',
                                           on_delete=models.CASCADE)
    porcentaje = models.BooleanField(default=False, help_text="Es porcentaje?")
    medible = models.BooleanField(default=True)
    meta_nombre = models.CharField(max_length=500, blank=True)
    meta_valor = models.PositiveSmallIntegerField(default=0, null=True)
    presupuesto = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True)

    class Meta:
        verbose_name = "Meta Plurianual"
        verbose_name_plural = "Meta Plurianual"

    def __str__(self):
        return self.nombre

    def metas_anuales_srt(self):
        """
        Metodo utilizado en reporte plan estrategico para obtener la meta correspondiente a cada periodo
        :return:
        """
        metas = []
        for p in self.resultado.objetivo_operativo.objetivo_estrategico.plan_estrategico.periodos.all():
            metas.append(MetaAnual.objects.filter(indicador=self, periodo=p).first())
            #metas = metas + "," + (m.periodo.nombre if m else '')
        return metas

class PlanOperativo(models.Model):
    """
    Modelo que permite almacenar un Poa por cada unidad académica del usuario,
    y que va a agrupar varios objetivos operativos asignados al cargo
    """
    activo = models.BooleanField(default=True)
    plan_estrategico = models.ForeignKey(PlanEstrategico, related_name='planes_operativos', on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoFiscal, related_name='planes_operativos', on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Plan Operativo Anual"
        verbose_name_plural = "Planes Operativos Anuales"
        ordering = ['periodo']
        unique_together = ('periodo',)
        #permissions = (('view_planoperativo', 'Puede ver Planes Operativos'),)

    def __str__(self):
        return 'POA %s ' % self.periodo

class MetaAnual(models.Model):
    '''
    Modelo para las metas de cada objetivo
    Nombre difetente del atributo Meta
    '''
    nombre = models.CharField(max_length=500, null=True)
    valor = models.PositiveSmallIntegerField(default=0, verbose_name="Alcance", blank=True)
    indicador = models.ForeignKey(Indicador, related_name='metas_anuales', on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoFiscal, related_name='metas_anuales', on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Meta Anual"
        verbose_name_plural = "Metas Anuales"
        ordering = ['indicador', 'periodo', 'nombre']
        unique_together = ('indicador', 'periodo',)

    def __str__(self):
        return self.nombre

    def get_plan_operativo(self):
        return PlanOperativo.objects.filter(periodo=self.periodo).first()

    def get_porcentaje_avance(self):
        return self.actividades.aggregate(total=models.Sum(F('progreso') * F('peso') / 100)).get('total') or 0


    def distribuir_porcentaje(self):
        """
        Permitir reasignar los porcentajes de peso que suponen cada actividad,
        en caso de que estas no tengan señalado un porcentaje fijo
        :return:
        """
        porcentaje = 100
        porcentaje -= self.actividades.filter(peso_fijo=True).aggregate(models.Sum('peso')).get('peso__sum') or 0
        sin_suma = self.actividades.filter(peso_fijo=False).count()
        if sin_suma:
            centinela = self.actividades.filter(peso_fijo=False).last()
            data = {'peso':
                        round(porcentaje/sin_suma)}
            self.actividades.filter(peso_fijo=False).exclude(id=centinela.id).update(**data)
            centinela.peso = porcentaje - (round(porcentaje/sin_suma) * (sin_suma-1))
            centinela.save()


    def get_porcentaje_disponible(self, actividad=None):
        porcentaje = 100
        if actividad:
            porcentaje -= self.actividades.filter(peso_fijo=True).exclude(id=actividad.id).aggregate(models.Sum('peso')).get(
                'peso__sum') or 0
        else:
            porcentaje -= self.actividades.filter(peso_fijo=True).aggregate(models.Sum('peso')).get('peso__sum') or 0
        # actividades = self.actividades.filter(peso_fijo=False).count()
        return porcentaje

    def get_porcentaje_para_nueva_actividad(self, ):
        return self.get_porcentaje_disponible()
