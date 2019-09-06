# -*- encoding: utf-8 -*-
import datetime

from django.db import models
from django.db.models import Q

from app.cientifica.models import ArticuloRevista, Ponencia, CapituloLibro, Libro
from app.core.models import CatalogoItem, PeriodoFiscal, PeriodoVacionesRelacionLaboral, PeriodoVacaciones
from app.core.models import Direccion
from app.core.utils import fecha
from app.organico.models import UAA
from app.seguridad.models import Usuario, AuditModel
from siaa.celery import app


class RegimenLaboral(models.Model):
    descripcion = models.TextField(null=True, blank=True)
    nombre = models.CharField(max_length=200)
    tipo_remuneracion = models.ForeignKey('core.CatalogoItem',
                                          null=True,
                                          related_name='tipo_remuneracion',
                                          limit_choices_to={'catalogo__codigo': 'TIPO_REMUNERACION'},
                                          on_delete=models.PROTECT)
    vacaciones = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Regímen laboral'
        verbose_name_plural = 'Regímenes laborales'

    def __str__(self):
        return str(self.nombre)


class GrupoOcupacional(models.Model):
    """
    Grupo ocupacional definido en el ministerio de relaciones laborales
    """
    grado = models.PositiveIntegerField()
    nivel = models.PositiveIntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=50)
    regimen_laboral = models.ForeignKey(RegimenLaboral, on_delete=models.PROTECT)
    rmu = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['regimen_laboral', 'grado', 'nombre']
        verbose_name = 'Grupo ocupacional'
        verbose_name_plural = 'Grupos ocupacionales'

    def __str__(self):
        if self.nivel:
            return str(self.nombre) + ' ' + str(self.nivel) + ' (' + str(self.regimen_laboral) + ') - $ ' + str(
                self.rmu)
        return str(self.nombre) + ' (' + str(self.regimen_laboral) + ') - $ ' + str(self.rmu)


class Puesto(models.Model):
    ambito_ejecucion = models.ForeignKey('core.CatalogoItem', null=True,
                                         related_name='ambito_ejecucion',
                                         limit_choices_to={'catalogo__codigo': 'AMBITO_EJECUCION'},
                                         on_delete=models.SET_NULL)
    anio_clasificacion_puesto = models.ForeignKey('core.CatalogoItem',
                                                  related_name='anio_clasificacion_puesto',
                                                  limit_choices_to={'catalogo__codigo': 'ANIO_CLASIFICACION_PUESTO'},
                                                  on_delete=models.PROTECT)
    area_conocimiento = models.TextField(blank=True, null=True)
    denominacion = models.CharField(max_length=200)
    denominacion_ministerio_finanzas = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.TextField(max_length=255, blank=True)
    especificidad_experiencia = models.TextField(blank=True, null=True)
    grupo_ocupacional = models.ForeignKey(GrupoOcupacional, on_delete=models.PROTECT)
    horas_dedicacion = models.PositiveSmallIntegerField(default=40)
    interfaz = models.TextField(blank=True, null=True)
    mision = models.TextField(blank=True, null=True)
    nivel_instruccion = models.ForeignKey('core.CatalogoItem',
                                          related_name='nivel_instruccion',
                                          limit_choices_to={'catalogo__codigo': 'NIVEL_INSTRUCCION'},
                                          on_delete=models.PROTECT)
    observaciones = models.TextField(blank=True, null=True)
    responsable_uaa = models.BooleanField(default=False)
    rol_puesto = models.ForeignKey('core.CatalogoItem',
                                   null=True,
                                   related_name='rol_puesto',
                                   limit_choices_to={'catalogo__codigo': 'ROL_PUESTO'},
                                   on_delete=models.SET_NULL)
    tiempo_experiencia = models.PositiveSmallIntegerField(blank=True, null=True)
    titulo_requerido = models.BooleanField(default=True)

    class Meta:
        ordering = ['-responsable_uaa', 'denominacion', ]

    def __str__(self):
        return str(self.denominacion) + " - " + str(self.grupo_ocupacional.rmu) + " (" + str(
            self.grupo_ocupacional.regimen_laboral.nombre) + ")"

    @staticmethod
    def buscar(criterio):
        """
        Busca los registros de acuerdo a los criterios por la denominación del puesto
        :param criterio:
        :return:
        """
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            for i in p_criterio:
                qset = qset & (Q(denominacion__icontains=i))
            return Puesto.objects.filter(qset).distinct()


class ActividadEsencial(models.Model):
    """
    Actividades esenciales de cada uno de los puestos
    """
    descripcion = models.TextField()
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)


class Conocimiento(models.Model):
    """
    Conocimientos que debe tener el puesto
    """
    descripcion = models.TextField()
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)


class Destreza(models.Model):
    """
    Destrezas, habilidades de puesto
    """
    descripcion = models.TextField()
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)


class UAAPuesto(models.Model):
    """
    Relación para ligar una Unidad Académico Administrativa con el Catalogo de Puesto
    """
    activo = models.BooleanField(default=True)
    puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    uaa = models.ForeignKey(UAA, on_delete=models.PROTECT)

    class Meta:
        ordering = ['uaa', 'puesto']

    def __str__(self):
        return str(self.uaa) + " - " + str(self.puesto) + " - " + str(self.puesto.grupo_ocupacional)

    @staticmethod
    def get_uaa_puestos_activos(uaa=None):
        """
        Devuelve los uua_puestos activos de una uaa
        :param uaa:
        :return:
        """
        return UAAPuesto.objects.filter(uaa=uaa, activo=True)

    @staticmethod
    def get_por_regimen_laboral_nombre(nombre=None):
        if nombre is None:
            return
        puestos = Puesto.objects.filter(grupo_ocupacional__regimen_laboral__nombre=nombre)
        return UAAPuesto.objects.filter(puesto__in=puestos, activo=True)

    @staticmethod
    def get_por_regimen_laboral(regimen_laboral=None):
        if regimen_laboral is None:
            return
        puestos = Puesto.objects.filter(grupo_ocupacional__regimen_laboral=regimen_laboral)
        return UAAPuesto.objects.filter(puesto__in=puestos, activo=True)

    @staticmethod
    def get_por_uaa_regimen_laboral_nombre(nombre=None, uaa=None):
        if nombre is None or uaa is None:
            return
        puestos = Puesto.objects.filter(grupo_ocupacional__regimen_laboral__nombre=nombre)
        return UAAPuesto.objects.filter(uaa=uaa, puesto__in=puestos, activo=True)

    @staticmethod
    def get_por_uaa_regimen_laboral(regimen_laboral=None, uaa=None):
        if regimen_laboral is None or uaa is None:
            return
        puestos = Puesto.objects.filter(grupo_ocupacional__regimen_laboral=regimen_laboral)
        return UAAPuesto.objects.filter(uaa=uaa, puesto__in=puestos, activo=True)

    def inactivar_uaa_puesto(self):
        self.activo = False
        self.save()
        for asignacion_puesto in self.asignacionpuesto_set.all():
            asignacion_puesto.verificar_vigencia()
        return


class AsignacionPuesto(models.Model):
    """
    Asignación de un funcionario a determinado puesto, donde un funcionario puede tener solo un
    puesto vigente y uno o varios activos.
    vigente, es el puesto que esta desempeñando actualmente.
    activo, son aquellos puestos que pueden asignarse como vigentes, es decir el funcionario en cualquier momento
    puede regresar a esta asignación de puesto. Adicional, solo son activos aquellos puestos donde la fecha de hoy
    se encuentra dentro de la fecha de inicio y fin o para aquellos puestos sin fecha de fin, la fecha de hoy tiene
    que ser mayor a la fecha de inicio.
    """
    activo = models.BooleanField(default=False)
    codigo = models.CharField(max_length=100,
                              verbose_name="Número de registro",
                              help_text="El número de registro ya sea de contrato o de nombramiento")
    encargado = models.BooleanField(default=False)
    factura = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                  help_text="Valor de factura en caso se pague por factura")
    fecha_fin = models.DateField(blank=True, null=True,
                                 verbose_name="Fecha de fin",
                                 help_text="La fecha donde termina el contrato o nombramiento")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio",
                                    help_text="La fecha de inicio del contrato o nombramiento")
    fecha_reconocimiento = models.DateField(verbose_name="Fecha de reconocimiento",
                                            help_text="La fecha de reconocimiento de tiempo de servicio", null=True,
                                            blank=True)
    fecha_termino = models.DateField(blank=True, null=True)

    funcionario = models.ForeignKey('talento_humano.Funcionario', related_name="asignaciones_puestos", on_delete=models.PROTECT)

    ingreso_concurso = models.BooleanField(default=False)

    orden = models.PositiveSmallIntegerField(blank=True, null=True)
    observacion = models.TextField(blank=True, max_length=400, null=True)
    partida_presupuestaria = models.CharField(max_length=200, null=True, blank=True,
                                              help_text='Partida general nominas')
    partida_individual = models.CharField(max_length=200, null=True, blank=True, help_text='Partida individual nominas')
    partida_individual_th = models.CharField(max_length=200, null=True, blank=True,
                                             help_text='Partida individual talento humano')
    uaa_puesto = models.ForeignKey('talento_humano.UAAPuesto', on_delete=models.PROTECT)
    termino = models.BooleanField(default=False)

    tipo_relacion_laboral = models.ForeignKey('core.CatalogoItem',
                                              null=True,
                                              related_name='tipo_relacion_laboral',
                                              limit_choices_to={'catalogo__codigo': 'TIPO_RELACION_LABORAL'},
                                              on_delete=models.PROTECT)
    tipo_terminacion = models.ForeignKey('core.CatalogoItem',
                                         null=True,
                                         blank=True,
                                         related_name='tipo_terminacion',
                                         limit_choices_to={'catalogo__codigo': 'TIPO_TERMINACION'},
                                         on_delete=models.PROTECT)
    vigente = models.BooleanField(default=False)

    class Meta:
        ordering = ['-activo', 'funcionario', 'uaa_puesto']

    @staticmethod
    def buscar(criterio, activo=None, vigente=None, regimen_laboral=None):
        """
        Devuelve la asignación de puestos de acuerdo al criterio, esta consulta
        lo hace por datos del funcionario o la denominación del puesto
        :param criterio: el criterio por el cual se va a buscar
        :return: el listado de asignación de puestos
        """
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            print(p_criterio)
            for i in p_criterio:
                print("qset", qset)
                qset = qset & (Q(funcionario__usuario__persona__primer_apellido__icontains=i) | Q(
                    funcionario__usuario__persona__segundo_apellido__icontains=i) | Q(
                    funcionario__usuario__persona__primer_nombre__icontains=i) | Q(
                    funcionario__usuario__persona__segundo_nombre__icontains=i) | Q(
                    funcionario__usuario__persona__numero_documento__icontains=i) | Q(
                    uaa_puesto__puesto__denominacion__icontains=i
                ))
            if activo:
                qset = qset & (Q(activo=True))
            if vigente:
                qset = qset & (Q(vigente=True))
            if regimen_laboral:
                uaa_puestos = UAAPuesto.get_por_regimen_laboral(regimen_laboral)
                qset = qset & (Q(uaa_puesto__in=uaa_puestos))
            print(qset)
        return AsignacionPuesto.objects.filter(qset).distinct()

    @staticmethod
    @app.task
    def reporte(criterio=None,
                fecha_fin_desde=None,
                fecha_fin_hasta=None,
                fecha_inicio_desde=None,
                fecha_inicio_hasta=None,
                fecha_termino_desde=None,
                fecha_termino_hasta=None,
                grupo_ocupacional=None,
                ingreso_concurso=None,
                puesto=None, uaa=None,
                regimen_laboral=None,
                responsable_uaa=None,
                tipo_terminacion=None,
                activo=None,
                encargado=None,
                termino=None,
                uaa_hijas=None,
                tipo_relacion_laboral=None,
                vigente=None,
                sexo=None,
                tipo_etnia=None,
                tipo_discapacidad=None,
                estado_civil=None
                ):
        qset = Q()
        if criterio:
            p_criterio = criterio.split(" ")
            for i in p_criterio:
                print("qset", qset)
                qset = qset & (Q(funcionario__usuario__persona__primer_apellido__icontains=i) | Q(
                    funcionario__usuario__persona__segundo_apellido__icontains=i) | Q(
                    funcionario__usuario__persona__primer_nombre__icontains=i) | Q(
                    funcionario__usuario__persona__segundo_nombre__icontains=i) | Q(
                    funcionario__usuario__persona__numero_documento__icontains=i) | Q(
                    uaa_puesto__puesto__denominacion__icontains=i
                ))
        if tipo_relacion_laboral:
            qset = qset & (Q(tipo_relacion_laboral=tipo_relacion_laboral))
        if tipo_terminacion:
            qset = qset & (Q(tipo_terminacion=tipo_terminacion))
        if activo is not None:
            qset = qset & (Q(activo=activo))
        if vigente is not None:
            qset = qset & (Q(vigente=vigente))
        if responsable_uaa is not None:
            qset = qset & (Q(uaa_puesto__puesto__responsable_uaa=responsable_uaa))
        if ingreso_concurso is not None:
            qset = qset & (Q(ingreso_concurso=ingreso_concurso))
        if termino is not None:
            qset = qset & (Q(termino=termino))
        if encargado is not None:
            qset = qset & (Q(encargado=encargado))
        if regimen_laboral:
            qset = qset & (Q(uaa_puesto__puesto__grupo_ocupacional__regimen_laboral=regimen_laboral))
        if puesto:
            qset = qset & (Q(uaa_puesto__puesto=puesto))
        if uaa:
            uaas = []
            if not uaa_hijas is None:
                if uaa_hijas:
                    uaas = uaa.get_uaa_hijas_todas()
            uaas.append(uaa)
            qset = qset & (Q(uaa_puesto__uaa__in=uaas))

        if grupo_ocupacional:
            qset = qset & (Q(uaa_puesto__puesto__grupo_ocupacional=grupo_ocupacional))
        if fecha_inicio_desde:
            qset = qset & (Q(fecha_inicio__gte=fecha_inicio_desde))
        if fecha_inicio_hasta:
            qset = qset & (Q(fecha_inicio__lte=fecha_inicio_hasta))
        if fecha_fin_desde:
            qset = qset & (Q(fecha_fin__gte=fecha_fin_desde))
        if fecha_fin_hasta:
            qset = qset & (Q(fecha_fin__lte=fecha_fin_hasta))
        if fecha_termino_desde:
            qset = qset & (Q(fecha_termino__gte=fecha_termino_desde))
        if fecha_termino_hasta:
            qset = qset & (Q(fecha_termino__lte=fecha_termino_hasta))

        if sexo is not None:
            qset = qset & (Q(funcionario__usuario__persona__sexo=sexo))
        if tipo_etnia is not None:
            qset = qset & (Q(funcionario__usuario__persona__tipo_etnia=tipo_etnia))
        if tipo_discapacidad is not None:
            if tipo_discapacidad == 'ninguna':
                qset = qset & (Q(funcionario__usuario__persona__tipo_discapacidad__isnull=True))
            else:
                qset = qset & (Q(funcionario__usuario__persona__tipo_discapacidad=tipo_discapacidad))
        if estado_civil is not None:
            qset = qset & (Q(funcionario__usuario__persona__estado_civil=estado_civil))

        return AsignacionPuesto.objects.filter(qset)

    def es_activo(self):
        if self.termino:
            if self.vigente:
                self.vigente = False
                self.save()
            return False
        hoy = datetime.date.today()
        if not self.fecha_fin:
            if self.fecha_inicio > hoy:
                return False
            else:
                return True
        else:
            if self.fecha_fin < hoy:
                self.vigente = False
                self.save()
                return False
            if self.fecha_fin < self.fecha_inicio:
                self.vigente = False
                self.save()
                return False
        if self.fecha_inicio > hoy:
            self.vigente = False
            self.save()
            return False
        if (self.fecha_inicio <= hoy) & (self.fecha_fin >= hoy):
            return True
        return False

    def fijar_vigente(self):
        """
        Fija como vigente una asignación de puesto siempre y cuando este activo
        :return:
        """
        for asignacion_puesto in self.funcionario.asignaciones_puestos.filter(vigente=True):
            asignacion_puesto.vigente = False
            asignacion_puesto.save()
        if self.es_activo():
            self.vigente = True
            self.save()
        return self.vigente

    def get_dias_laborados(self, periodo_vacaciones):
        # JJM 2019-01-31 utilizo metodo de clase FechaUtil
        # fecha_inicial = periodo_vacaciones.fecha_inicio
        # fecha_final = periodo_vacaciones.fecha_fin
        #
        # if periodo_vacaciones.fecha_inicio < self.fecha_inicio:
        #     fecha_inicial = self.fecha_inicio
        # if self.fecha_fin is not None:
        #     if periodo_vacaciones.fecha_fin > self.fecha_fin:
        #         fecha_final = self.fecha_fin
        fecha_inicial = fecha.fecha_mayor(self.fecha_inicio, periodo_vacaciones.fecha_inicio)
        fecha_final = fecha.fecha_menor(self.fecha_termino, self.fecha_fin)
        fecha_final = fecha.fecha_menor(fecha_final, periodo_vacaciones.fecha_fin)

        dia_inicial = fecha_inicial.day
        dia_final = fecha_final.day
        if dia_final - dia_inicial < 27:
            return dia_final - dia_inicial
        return 0

    @staticmethod
    def get_asignacion_responsable(uaa, vigente=True):
        if not isinstance(uaa, UAA):
            return None
        return AsignacionPuesto.objects.filter(vigente=vigente, uaa_puesto__uaa=uaa,
                                               uaa_puesto__puesto__responsable_uaa=True)

    def get_formacion_academica_persona(self):
        return FormacionAcademica.get_formacion_academicas(self.get_persona())

    def get_duracion(self, reconocimiento=False):
        fecha_inicial = self.fecha_inicio
        if reconocimiento:
            if self.fecha_reconocimiento:
                fecha_inicial = self.fecha_reconocimiento

        fecha_final = datetime.date.today()
        if self.fecha_fin:
            if self.fecha_fin < datetime.date.today():
                fecha_final = self.fecha_fin
        if self.fecha_termino:
            fecha_final = self.fecha_termino

        mes_inicial = fecha_inicial.month
        mes_final = fecha_final.month
        dia_inicial = fecha_inicial.day
        dia_final = fecha_final.day
        anios = fecha_final.year - fecha_inicial.year
        if dia_final < dia_inicial:
            dia_final = dia_final + 30
            mes_final = mes_final - 1
        if mes_final < mes_inicial:
            mes_final = mes_final + 12
            anios = anios - 1
        meses = mes_final - mes_inicial
        dias = dia_final - dia_inicial
        return anios, meses, dias

    def get_duracion_info(self):
        anios, meses, dias = self.get_duracion(reconocimiento=True);

        a = " años\n"
        m = " meses\n"
        d = " dias\n"

        if anios == 0 or meses == 1 or anios == 1:
            if meses == 1:
                m = " mes  "
            if anios == 1:
                a = " año "
            if anios == 0:
                return str(meses) + m + str(dias) + d
        return str(anios) + a + str(meses) + m + str(dias) + d

    def get_duracion_recocimiento(self):
        """
        Devuelve la duración de tiempo desde la fecha de reconcimento en caso lo tuviera
        :return: 
        """
        if self.fecha_reconocimiento:
            return self.get_duracion(reconocimiento=True)
        return None

    def get_meses_laborados(self, periodo_vacaciones):

        fecha_inicial = fecha.fecha_mayor(self.fecha_inicio, periodo_vacaciones.fecha_inicio)
        fecha_final = fecha.fecha_menor(self.fecha_termino, self.fecha_fin)
        fecha_final = fecha.fecha_menor(fecha_final, periodo_vacaciones.fecha_fin)
        return fecha.diferencia_meses(fecha_inicial, fecha_final)
        # JJM 2019-01-30 comento calculo anterior, para tomar en cuenta fecha termino de asignacion
        #
        # fecha_inicial = periodo_vacaciones.fecha_inicio
        # fecha_final = periodo_vacaciones.fecha_fin
        # if periodo_vacaciones.fecha_inicio < self.fecha_inicio:
        #     fecha_inicial = self.fecha_inicio
        # if self.fecha_fin is not None:
        #     if periodo_vacaciones.fecha_fin > self.fecha_fin:
        #         fecha_final = self.fecha_fin
        # mes_inicial = fecha_inicial.month
        # mes_final = fecha_final.month
        # meses = 0
        # if fecha_inicial.year < fecha_final.year:
        #     mes_final = mes_final + 12
        # if mes_final > mes_inicial:
        #     meses = mes_final - mes_inicial
        # dia_inicial = fecha_inicial.day
        # dia_final = fecha_final.day
        # #OJO SE LE CAMBIO DE > A >= 27 x el caso del contratos que son definidos desde  1 Enero al 28 de Febrero
        # if dia_final - dia_inicial >= 27:
        #     meses = meses + 1
        # return meses

    def get_observaciones_extendidas(self):
        if self.termino:
            return str(self.observacion) + ' Termino el: ' + str(self.fecha_termino) + ' por: ' + str(
                self.tipo_terminacion)
        return self.observacion

    @staticmethod
    def get_por_regimen_laboral(regimen_laboral=None, vigente=True):
        """
        Obtiene las asignaciones de puesto de acuerdo al nombre del regimen lan¿boral LOES, LOSEP etc
        :param nombre:
        :return:
        """
        if regimen_laboral is None:
            return None
        uaa_puestos = UAAPuesto.get_por_regimen_laboral(regimen_laboral)
        return AsignacionPuesto.objects.filter(uaa_puesto__in=uaa_puestos, vigente=vigente)

    @staticmethod
    def get_por_regimen_laboral_(regimen_laboral=None, uaa=None, vigente=True):
        """
        Obtiene las asignaciones de puesto de acuerdo al nombre del regimen laboral LOES, LOSEP etc
        y a una unidad académica administrativo
        :param nombre:
        :return:
        """
        if regimen_laboral is None or uaa is None:
            return None
        uaa_puestos = UAAPuesto.get_por_uaa_regimen_laboral(regimen_laboral=regimen_laboral, uaa=uaa)
        return AsignacionPuesto.objects.filter(uaa_puesto__in=uaa_puestos)

    @staticmethod
    def get_por_regimen_laboral_nombre(nombre=None):
        """
        Obtiene las asignaciones de puesto de acuerdo al nombre del regimen lan¿boral LOES, LOSEP etc
        :param nombre:
        :return:
        """
        if nombre is None:
            return None
        uaa_puestos = UAAPuesto.get_por_regimen_laboral_nombre(nombre)
        return AsignacionPuesto.objects.filter(uaa_puesto__in=uaa_puestos)

    @staticmethod
    def get_por_uaa_regimen_laboral_nombre(nombre=None, uaa=None, vigente=True):
        """
        Obtiene las asignaciones de puesto de acuerdo al nombre del regimen lan¿boral LOES, LOSEP etc
        :param nombre:
        :return:
        """
        if nombre is None or uaa is None:
            return None
        uaa_puestos = UAAPuesto.get_por_uaa_regimen_laboral_nombre(nombre=nombre, uaa=uaa)
        return AsignacionPuesto.objects.filter(uaa_puesto__in=uaa_puestos, vigente=vigente)

    def get_persona(self):
        return self.funcionario.usuario.persona

    def get_puesto(self):
        return self.uaa_puesto.puesto.denominacion

    def get_sueldo(self):
        """
        Devuelve la remuneración, 
        si es por servicios profesionales devuelve el valor de la factura,
        Si tiene un solo puesto activo devuelve el valor de ese puesto
        Si tiene mas de un puesto activo devuelve el valor más alto
        :return: 
        """
        if self.factura:
            return self.factura
        sueldo = self.uaa_puesto.puesto.grupo_ocupacional.rmu
        # JJM 2018-12-10 comento porque no devuelve el sueldo real en puestos inactivos.
        # for asignacion in self.funcionario.get_asignacion_puesto_activos(activo=True):
        #    sueldo_2 = asignacion.uaa_puesto.puesto.grupo_ocupacional.rmu
        #    if sueldo < sueldo_2:
        #        sueldo = sueldo_2
        # JJM 2018-12-10 fin comentado
        return sueldo

    def get_uaa(self):
        return self.uaa_puesto.uaa.nombre

    def puesto(self):
        return self.uaa_puesto.puesto

    def terminacion_asignacion_puesto(self):
        self.termino = True
        # self.fecha_termino = datetime.date.today()
        self.save()
        # JJM recalculo vacaciones de esta asignacion
        for vacacion in self.vacaciones_set.filter(activo=True):
            vacacion.recalcular_vacaciones()
        self.verificar_vigencia()
        return

    def uaa(self):
        return self.uaa_puesto.uaa

    def ubicar_funcionario(self):
        """
        Ubica el funcionario de acuerdo a la asignación de puesto
        :return: asignación de puesto actualizado
        """
        if self.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre == 'LOES':
            self.funcionario.activar_como_docente()

        if self.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre == 'LOSEP':
            self.funcionario.activar_como_administrativo()

        if self.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.nombre == 'Código de Trabajo':
            self.funcionario.activar_como_trabajador()
        self.funcionario.es_funcionario_activo()
        return

    def verificar_vigencia(self):
        # Si es puesto no esta activo, entonces activo y vigente es false
        if not self.uaa_puesto.activo:
            self.activo = False
            self.vigente = False
            self.save()
            self.ubicar_funcionario()
            return
        # Si tiene la asignación de puesto termino, entonces activo y vigente es false
        if self.termino:
            self.activo = False
            self.vigente = False
        else:
            self.activo = self.es_activo()
        self.save()

        count = self.funcionario.asignaciones_puestos.filter(activo=True).count()
        # Si tiene solo un puesto activo, y este corresponde al activo entonces se convierte en vigente, caso contrario
        # se debera fijar la vigencia al puesto que compete. Con el metodo fijar_vigente, nos aseguramos que exista solo
        # un puesto vigente
        if count == 1 and self.activo:
            self.fijar_vigente()
            # self.vigente = True
            # self.save()
        self.ubicar_funcionario()
        return

    @staticmethod
    @app.task
    def reporte_general(
            edad=None,
            activo=None,
            puesto=None,
            regimen_laboral=None,
            tipo_relacion_laboral=None,
    ):
        qset = Q()

        if activo is not None:
            qset = qset & (Q(activo=activo))
        if tipo_relacion_laboral:
            qset = qset & (Q(tipo_relacion_laboral=tipo_relacion_laboral))
        if regimen_laboral:
            qset = qset & (Q(uaa_puesto__puesto__grupo_ocupacional__regimen_laboral=regimen_laboral))
        if edad is not None:
            if edad == 0:
                edad = None
            else:
                dia_actual = datetime.date.today()
                fecha_nacimiento = dia_actual.replace(year=dia_actual.year - edad)
                # qset= qset & (Q(funcionario__usuario__persona__fecha_nacimiento__year__lte= anio)&Q(funcionario__usuario__persona__fecha_nacimiento__month__lte= mes)&Q(funcionario__usuario__persona__fecha_nacimiento__day__lte= dia))
                qset = qset & (Q(funcionario__usuario__persona__fecha_nacimiento__lte=str(fecha_nacimiento)))
            # qset = qset & (Q(funcionario__usuario__persona__fecha_nacimiento__range__gte= (datetime.date(1918,1,1),fecha_nacimiento)))
        if puesto:
            qset = qset & (Q(uaa_puesto__puesto=puesto))

        return AsignacionPuesto.objects.filter(qset)

    def __str__(self):
        puesto_fecha_inicio = str(self.fecha_inicio)
        puesto_fecha_fin = str(self.fecha_fin)
        puesto_uaa = str(self.uaa_puesto.uaa.nombre)
        puesto_uaa_puesto = str(self.uaa_puesto.puesto.denominacion)
        return ' %s : %s,  %s - %s ' % (puesto_uaa,
                                        puesto_uaa_puesto,
                                        puesto_fecha_inicio,
                                        puesto_fecha_fin)


class TrayectoriaLaboralExterna(models.Model):

    funcionario = models.ForeignKey('talento_humano.Funcionario', related_name="trayectorias_laborales_externas",
                                    on_delete=models.CASCADE)
    institucion = models.CharField(max_length=200)
    unidad_administrativa = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo_ingreso = models.ForeignKey('core.CatalogoItem',
                                       related_name='motivo_ingreso',
                                       limit_choices_to={'catalogo__codigo': 'MOTIVO_INGRESO'},
                                       on_delete=models.PROTECT)
    motivo_salida = models.ForeignKey('core.CatalogoItem',
                                      related_name='motivo_salida',
                                      limit_choices_to={'catalogo__codigo': 'MOTIVO_SALIDA'},
                                      on_delete=models.PROTECT)
    puesto = models.CharField(max_length=200)
    tipo_institucion = models.ForeignKey('core.CatalogoItem',
                                         related_name='tipo_institucion',
                                         limit_choices_to={'catalogo__codigo': 'TIPO_INSTITUCION'},
                                         on_delete=models.PROTECT)

    class Meta:
        ordering = ('fecha_inicio',)

    def __str__(self):
        return 'Trayectoria Laboral (Externa): %s-%s' % (self.puesto, self.institucion)


class EvaluacionDesempenio(models.Model):

    funcionario = models.ForeignKey('talento_humano.Funcionario', related_name="evaluaciones_desempenio", on_delete=models.CASCADE)
    asignacion_puesto = models.ForeignKey('talento_humano.AsignacionPuesto', related_name="evaluaciones_desempenio", on_delete=models.PROTECT)
    fecha_evaluacion_inicio = models.DateField()
    fecha_evaluacion_fin = models.DateField()
    puntaje = models.PositiveSmallIntegerField()
    calificacion = models.ForeignKey('core.CatalogoItem',
                                     related_name='calificacion',
                                     limit_choices_to={'catalogo__codigo': 'CALIFICACION'}, on_delete=models.PROTECT)

    class Meta:
        ordering = ('fecha_evaluacion_inicio',)

    def __str__(self):
        return '%s-%s' % (self.puntaje, self.calificacion)


class FormacionAcademica(models.Model):

    area_conocimiento = models.CharField(max_length=200)
    clasificacion = models.CharField(max_length=100, blank=True, null=True)
    egresado = models.BooleanField(default=False)
    expediente = models.ForeignKey('core.Expediente', on_delete=models.CASCADE)
    fecha_grado = models.DateField(null=True)
    fecha_registro = models.DateField(null=True)
    institucion_educativa = models.ForeignKey('core.InsitucionEducativa',
                                              blank=True, null=True,
                                              related_name='institucion_educativa', on_delete=models.SET_NULL)
    institucion_educativo_otro = models.CharField(max_length=200, blank=True, null=True)
    nivel_instruccion = models.ForeignKey('core.CatalogoItem',
                                          related_name='nivel_instruccion_th',
                                          limit_choices_to={'catalogo__codigo': 'NIVEL_INSTRUCCION'},
                                          on_delete=models.PROTECT)
    numero_registro = models.CharField(max_length=50, blank=True)
    observacion = models.CharField(max_length=200, blank=True, null=True)
    pais = models.ForeignKey('core.Pais', null=True, on_delete=models.PROTECT)
    periodos_aprobados = models.PositiveSmallIntegerField(null=True)
    tipo_periodo_estudio = models.ForeignKey('core.CatalogoItem',
                                             related_name='tipo_periodo_estudio',
                                             limit_choices_to={'catalogo__codigo': 'TIPO_PERIODO_ESTUDIO'},
                                             null=True, on_delete=models.PROTECT)
    tipo_titulo = models.ForeignKey('core.CatalogoItem',
                                    related_name='tipo_titulo',
                                    limit_choices_to={'catalogo__codigo': 'TIPO_TITULO'}, null=True, on_delete=models.SET_NULL)
    titulo_obtenido = models.CharField(max_length=300, blank=True)
    validado_bsg = models.BooleanField(default=False)

    class Meta:
        ordering = ('nivel_instruccion',)

    def __str__(self):
        titulo = self.titulo_obtenido
        nombres = self.expediente.persona.get_nombres_completos()
        return 'Formacion  Titulo:%s, Nombres:%s' % (titulo, nombres)

    @staticmethod
    def get_formacion_academicas(persona=None):
        """
        Devuelve la formación académica de una persona
        :param persona: la persona a consultar
        :return: las formaciones academicas
        """
        if persona is None:
            return None
        return FormacionAcademica.objects.filter(expediente__persona=persona)


class DeclaracionBienes(models.Model):

    expediente = models.ForeignKey('core.Expediente', on_delete=models.CASCADE)
    fecha_declaracion = models.DateField()
    lugar_notaria = models.ForeignKey('core.CatalogoItem',
                                      related_name='lugar_notaria',
                                      limit_choices_to={'catalogo__codigo': 'LUGAR_NOTARIA'}, on_delete=models.PROTECT)
    numero_notaria = models.TextField(max_length=200)


class InformacionBancaria(models.Model):

    codigo = models.CharField(max_length=140, default="1")
    expediente = models.ForeignKey('core.Expediente', on_delete=models.CASCADE)
    institucion_financiera = models.ForeignKey('core.CatalogoItem',
                                               related_name='institucion_financiera',
                                               limit_choices_to={'catalogo__codigo': 'INSTITUCION_FINANCIERA'},on_delete=models.PROTECT)
    numero_cuenta = models.CharField(max_length=100)
    principal = models.BooleanField(default=False, blank=True)
    tipo_cuenta = models.ForeignKey('core.CatalogoItem', related_name='tipo_cuenta',
                                    limit_choices_to={'catalogo__codigo': 'TIPO_CUENTA'}, on_delete=models.PROTECT)


class Capacitacion(models.Model):

    auspiciante = models.CharField(max_length=250)
    certificado_por = models.CharField(max_length=250)
    evento = models.CharField(max_length=250)
    expediente = models.ForeignKey('core.Expediente', on_delete=models.CASCADE)
    fecha_fin = models.DateField()
    fecha_inicio = models.DateField()
    horas = models.PositiveSmallIntegerField()
    pais = models.ForeignKey('core.Pais', on_delete=models.PROTECT)
    validado = models.BooleanField(default=False, blank=True)
    tipo_evento = models.ForeignKey('core.CatalogoItem',
                                    related_name='tipo_evento',
                                    limit_choices_to={'catalogo__codigo': 'TIPO_EVENTO_CAPACITACION'}
                                    , on_delete=models.PROTECT)
    tipo_certificacion = models.ForeignKey('core.CatalogoItem',
                                           related_name='tipo_certificacion',
                                           limit_choices_to={'catalogo__codigo': 'TIPO_CERTIFICACION'}
                                           , on_delete=models.PROTECT)


class Funcionario(AuditModel):

    activo = models.BooleanField(default=False)
    usuario = models.OneToOneField('seguridad.Usuario', on_delete=models.CASCADE)

    class Meta:
        ordering = ['usuario__persona']

    def __str__(self):
        return str(self.usuario.persona)

    def activar_como_administrativo(self):
        if self.es_docente():
            self.docente.activo = False
            self.docente.save()
        if self.es_trabajador():
            self.trabajador.activo = False
            self.trabajador.save()
        if not self.es_administrativo():
            if self.tiene_administrativo():
                self.administrativo.activo = True
                self.administrativo.save()
            else:
                administrativo = Administrativo(funcionario=self, activo=True)
                administrativo.save()
        return

    def activar_como_docente(self):
        if self.es_administrativo():
            self.administrativo.activo = False
            self.administrativo.save()
        if self.es_trabajador():
            self.trabajador.activo = False
            self.trabajador.save()
        if not self.es_docente():
            if self.tiene_docente():
                self.docente.activo = True
                self.docente.save()
            else:
                docente = Docente(funcionario=self, activo=True)
                docente.save()
        return

    def activar_como_trabajador(self):
        if self.es_administrativo():
            self.administrativo.activo = False
            self.administrativo.save()
        if self.es_docente():
            self.docente.activo = False
            self.docente.save()
        if not self.es_trabajador():
            if self.tiene_trabajador():
                self.trabajador.activo = True
                self.trabajador.save()
            else:
                trabajador = Trabajador(funcionario=self, activo=True)
                trabajador.save()
        return

    @staticmethod
    def buscar(criterio):
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            for i in p_criterio:
                qset = qset & (Q(usuario__persona__primer_apellido__icontains=i) | Q(
                    usuario__persona__segundo_apellido__icontains=i) | Q(
                    usuario__persona__primer_nombre__icontains=i) | Q(
                    usuario__persona__segundo_nombre__icontains=i) | Q(
                    usuario__persona__numero_documento__icontains=i))
        return Funcionario.objects.filter(qset).distinct()

    @staticmethod
    def buscar_avanzado(criterio, vigente=None, activo=None):
        """
        Busca por funcionarios activos
        :param criterio:
        :return:
        """
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            for i in p_criterio:
                qset = qset & (Q(usuario__persona__primer_apellido__icontains=i) | Q(
                    usuario__persona__segundo_apellido__icontains=i) | Q(
                    usuario__persona__primer_nombre__icontains=i) | Q(
                    usuario__persona__segundo_nombre__icontains=i) | Q(
                    usuario__persona__numero_documento__icontains=i) | Q(
                    asignaciones_puestos__uaa_puesto__puesto__denominacion__icontains=i) | Q(
                    asignaciones_puestos__uaa_puesto__uaa__nombre__icontains=i)
                               )
        if not vigente is None:
            qset = qset & Q(asignaciones_puestos__vigente=vigente)
        if not activo is None:
            qset = qset & Q(asignaciones_puestos__activo=activo)
        return Funcionario.objects.filter(qset).distinct()

    def es_administrativo(self):
        if hasattr(self, 'administrativo'):
            return self.administrativo.activo
        return False

    def es_docente(self):
        if hasattr(self, 'docente'):
            return self.docente.activo
        return False

    def es_funcionario_activo(self):
        """
        Valida si el funcionario teien asgnaciones de puesto vigente y lo activa
        """

        for asignacion_puesto in self.asignaciones_puestos.all():
            # asignacion_puesto.verificar_vigencia()
            if asignacion_puesto.vigente:
                self.activo = True
                self.save()
                return True
        self.inactivar_funcionario()
        return False

    def es_responsable_uaa(self, nombre_tipo_uaa=None):
        if nombre_tipo_uaa is None:
            return False
        asignacio_puesto = self.get_asignacion_puesto_vigente()
        if asignacio_puesto:
            tipo_uaa = CatalogoItem.get_catalogo_item_nombre('TIPO_UAA', nombre_tipo_uaa)
            if asignacio_puesto.uaa_puesto.uaa.tipo_uaa == tipo_uaa:
                if asignacio_puesto.uaa_puesto.puesto.responsable_uaa:
                    return True
        return False

    def es_trabajador(self):
        if hasattr(self, 'trabajador'):
            return self.trabajador.activo
        return False

    def get_apellidos(self):
        return self.usuario.persona.get_apellidos()

    def get_asignacion_puesto_activos(self, activo=None):
        """
        Obtiene la asignación de puesto que este activa
        """
        if activo is None:
            activo = True
        return AsignacionPuesto.objects.filter(Q(funcionario=self) & Q(activo=activo))

    def get_asignacion_puesto_vigente(self):
        """
        Obtiene la asignación de puesto que este vigente
        """
        return AsignacionPuesto.objects.filter(Q(funcionario=self) & Q(vigente=True)).first()

    def get_ultimo_asignacion_puesto(self):
        return AsignacionPuesto.objects.filter(Q(funcionario=self)).order_by('-fecha_inicio', '-fecha_fin').first()

    def get_asignacion_puestos_funcionario(self):
        """
        Obtiene la asignación de puesto que tenga un funcionario
        """
        return AsignacionPuesto.objects.filter(Q(funcionario=self) & Q(vigente=False)).all()

    def get_disponibles_vacacion(self):
        vacaciones = Vacaciones.objects.filter(funcionario=self, dias_pendientes__gt=0)
        count = 0
        for vacacion in vacaciones:
            horas_dias = vacacion.horas_pendientes * 0.0417;
            minutos_dias = vacacion.minutos_pendientes * 0.000694;
            count = count + vacacion.dias_pendientes + horas_dias + minutos_dias
        return count

    def get_foto_url(self):
        return self.usuario.foto_url

    def get_periodo_vacaciones(self, activo=None):
        """
        Devuelve el periodo de vacación de la asignación de puesto vigente, para los inactivos tambien se
         debe mostrar para revisar el periodo de vacaciones y registrar su liquidacion.
        :param activo: 
        :return: 
        """
        asignacion_puesto = self.get_asignacion_puesto_vigente()

        if asignacion_puesto is None:
            asignacion_puesto = self.get_ultimo_asignacion_puesto()

        # if not activo is None:
        if not asignacion_puesto is None:
            periodo_vaciones_relacion_laboral = PeriodoVacionesRelacionLaboral.get_periodos_vacaciones_activos(
                asignacion_puesto.tipo_relacion_laboral, activo).first()
            if periodo_vaciones_relacion_laboral:
                return periodo_vaciones_relacion_laboral.periodo_vacaciones

    @staticmethod
    def get_funcionarios_activos(vigente=None):
        """
        Obtiene todos los funcionarios con asignación de puesto activo
        :return:
        """
        if not vigente is None:
            return Funcionario.objects.filter(asignaciones_puestos__activo=True, asignaciones_puestos__vigente=vigente)
        return Funcionario.objects.filter(asignaciones_puestos__activo=True)

    @staticmethod
    def get_funcionario_numero_documento(numero_documento):
        """
        Este método obtiene un funcionario, si no existe lo crea
        :param numero_documento:
        :return:
        """
        funcionario = Funcionario.objects.filter(usuario__persona__numero_documento=numero_documento).first()
        if funcionario:
            return funcionario
        usuario = Usuario.get_usuario_numero_documento(numero_documento)
        if usuario:
            funcionario = Funcionario(usuario=usuario)
            funcionario.save()
            print('funcionario', funcionario)
            return funcionario
        return None

    @staticmethod
    def get_funcionarios_uaa(uaa, activo=None, vigente=True, regimen_laboral=None):
        """
        Obtiene el listado de funcionarios en determinada UAA, opcional activo y vigente
        :param uaa:
        :param activo:
        :param vigente:
        :return:
        """
        if uaa is None:
            return
        qset = Q()
        if not activo is None:
            qset = qset & Q(asignacionpuesto__activo=True)
        if not activo is None:
            qset = qset & Q(asignacionpuesto__vigente=True)
        if not regimen_laboral is None:
            qset = qset & Q(asignacionpuesto__uaa_puesto__puesto__grupo_ocupacional__regimen_laboral=regimen_laboral)
        qset = qset & Q(asignacionpuesto__uaa_puesto__uaa=uaa)
        return Funcionario.objects.filter(qset).distinct()

    @staticmethod
    def get_funcionarios_vigentes():
        """
        Obtiene todos los funcionarios con asgnación de puesto vigente
        """
        return Funcionario.objects.filter(asignaciones_puestos__vigente=True)

    def get_vacaciones(self):
        """
        devuelve o crea registro de vacaciones
        :return:
        """
        periodo_vacaciones = self.get_periodo_vacaciones(activo=True)
        vacaciones = Vacaciones.objects.filter(Q(funcionario=self) & Q(periodo_vacaciones=periodo_vacaciones)).first()
        if not vacaciones and periodo_vacaciones:
            asignacion_puesto = self.get_asignacion_puesto_vigente()
            dias_limite = asignacion_puesto.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.vacaciones
            variable = dias_limite / 12
            dias = asignacion_puesto.get_meses_laborados(periodo_vacaciones) * variable
            dias = dias + asignacion_puesto.get_dias_laborados(periodo_vacaciones) / 100 * variable
            horas = abs(dias) - abs(int(dias))
            horas = horas * 8
            vacaciones = Vacaciones(activo=True, funcionario=self, periodo_vacaciones=periodo_vacaciones,
                                    asignacion_puesto=asignacion_puesto,
                                    dias_totales=dias, dias_pendientes=dias, horas_totales=horas,
                                    horas_pendientes=horas)
            vacaciones.save()

            # Genera compensación de dias para vacaciones anteriores y nuevas
            vacacionesAnteriores = Vacaciones.objects.filter(Q(funcionario_id=self.id) & (
                        Q(dias_pendientes__gt=0) | Q(horas_pendientes__gt=0) | Q(minutos_pendientes__gt=0)) & Q(
                activo=True))
            for vacAnterior in vacacionesAnteriores:
                if vacAnterior.dias_pendientes > 0 or vacAnterior.horas_pendientes > 0 or vacAnterior.minutos_pendiente > 0:
                    # vacAnterior.activo = False
                    compensacionAnt = CompensacionDias(vacaciones=vacAnterior,
                                                       horas=vacAnterior.horas_pendientes * -1,
                                                       dias=vacAnterior.dias_pendientes * -1,
                                                       minutos=vacAnterior.minutos_pendientes * -1,
                                                       observacion='Vacaciones pendientes a: ' + vacaciones.periodo_vacaciones.nombre)

                    compensacionNew = CompensacionDias(vacaciones=vacaciones,
                                                       horas=vacAnterior.horas_pendientes,
                                                       dias=vacAnterior.dias_pendientes,
                                                       minutos=vacAnterior.minutos_pendientes,
                                                       observacion='Vacaciones pendientes de: ' + vacAnterior.periodo_vacaciones.nombre)

                    compensacionAnt.save()
                    compensacionNew.save()
                    vacAnterior.recalcular_dias_pendientes()
                    vacAnterior.activo = False
                    vacAnterior.save()
            vacaciones.recalcular_dias_pendientes()

        return vacaciones

    def get_nombres(self):
        return self.usuario.persona.get_nombres()

    def inactivar_funcionario(self):
        if self.es_administrativo():
            self.administrativo.activo = False
            self.administrativo.save()
        if self.es_docente():
            self.docente.activo = False
            self.docente.save()
        if self.es_trabajador():
            self.trabajador.activo = False
            self.trabajador.save()
        self.activo = False
        self.save()
        return

    def tiene_administrativo(self):
        if hasattr(self, 'administrativo'):
            return True
        return False

    def tiene_docente(self):
        if hasattr(self, 'docente'):
            return True
        return False

    def tiene_trabajador(self):
        if hasattr(self, 'trabajador'):
            return True
        return False

    def tiene_vacacion(self):
        """
        Devuelve verdader o falso en caso de que tenga o no tenga vacaciones
        :return: Verdareo o Falso según corresponda
        """
        periodo_vacaciones = self.get_periodo_vacaciones(activo=True)
        if not periodo_vacaciones:
            return False
        vacaciones = Vacaciones.objects.filter(Q(funcionario=self) & Q(periodo_vacaciones=periodo_vacaciones))
        print(vacaciones.count())
        if vacaciones.count() > 0:
            return True
        return False

    def valida_capacitacion(self):
        '''
        Valida si existe al menos una capacitación para docentes y administrativos, caso contrario si es trabajador es opcional
        :return:
        '''
        capacitacion = Capacitacion.objects.filter(expediente__persona=self.usuario.persona).first()
        if self.es_trabajador() or (not self.es_trabajador() and capacitacion):
            return True
        return False

    def valida_datos_personales(self):
        '''
        Valida si existe toda la información personal, declaración de bienes e información bancaria
        :return:
        '''
        p = self.usuario.persona
        if p.sexo and p.fecha_nacimiento and p.tipo_sangre and p.estado_civil and p.nacionalidad and p.tipo_etnia and p.expediente:
            informacion_bancaria = InformacionBancaria.objects.filter(expediente=p.expediente).first()
            declaracion_bienes = DeclaracionBienes.objects.filter(expediente=p.expediente).first()
            if informacion_bancaria and declaracion_bienes:
                return True
        return False

    def valida_direccion(self):
        '''
        Valida si existe una direccion de domicio y trabajo, con telefono y celular obligatorios y validados
        :return:
        '''
        from app.core.models import CatalogoItem, Direccion
        tipo1 = CatalogoItem.objects.filter(catalogo__codigo='TIPO_DIRECCION', nombre='Domicilio').first()
        tipo2 = CatalogoItem.objects.filter(catalogo__codigo='TIPO_DIRECCION', nombre='Trabajo').first()
        direccion1 = Direccion.objects.filter(tipo_direccion=tipo1, persona=self.usuario.persona).first()
        direccion2 = Direccion.objects.filter(tipo_direccion=tipo2, persona=self.usuario.persona).first()
        if direccion1 and direccion2:
            direcciones = Direccion.objects.filter(Q(persona=self.usuario.persona)).all()
            for direccion in direcciones:
                if not direccion.validar_telefono() or not direccion.validar_celular() or direccion.parroquia is None:
                    return False
            return True
        return False

    def get_direccion_oficina(self):
        oficina = CatalogoItem.objects.filter(catalogo__codigo='TIPO_DIRECCION', nombre='Oficina').first()
        return Direccion.objects.filter(tipo_direccion=oficina, persona=self.usuario.persona).first()

    def valida_formacion(self):
        '''
        Valida, los registros de formación academica deben tener completos todos los campos
        :return:
        '''
        formacion = FormacionAcademica.objects.filter(Q(expediente__persona=self.usuario.persona) &
                                                      (Q(pais=None) | Q(periodos_aprobados=None) | Q(
                                                          tipo_periodo_estudio=None) | Q(area_conocimiento=None) | Q(
                                                          area_conocimiento='')))
        if formacion.count() > 0:
            return False
        else:
            return True

    def valida_relacion(self):
        '''
        Valida si tiene mínimo una relación ingresada de contacto con telefono y celular completos
        :return:
        '''
        from app.core.models import Relacion
        relacion = Relacion.objects.filter(Q(expediente__persona=self.usuario.persona) & Q(contacto=True) &
                                           ~Q(telefono=None) & ~Q(celular=None) & ~Q(telefono='') & ~Q(
            celular='')).first()
        if relacion:
            return True
        else:
            return False

    def valida_produccion_cientifica(self):
        '''
        Valida si tiene mínimo una producción cientifica los docentes, caso contrario es opcional
        :return:
        '''
        if not self.es_docente():
            return True
        else:
            articulo_revista = ArticuloRevista.objects.filter(
                produccion_cientifica__expediente__persona=self.usuario.persona).first()
            ponencia = Ponencia.objects.filter(produccion_cientifica__expediente__persona=self.usuario.persona).first()
            if articulo_revista or ponencia:
                return True
            else:
                libro = Libro.objects.filter(produccion_cientifica__expediente__persona=self.usuario.persona).first()
                capituloLibro = CapituloLibro.objects.filter(
                    produccion_cientifica__expediente__persona=self.usuario.persona).first()
                if libro or capituloLibro:
                    return True
            return False

    def valida_trayectoria_laboral(self):
        '''
        Valida si tiene mínimo una trayectoria laboral ya sea interna o externa
        :return:
        '''
        trayectoria_externa = TrayectoriaLaboralExterna.objects.filter(funcionario=self).first()
        if trayectoria_externa:
            return True
        return False


class Administrativo(models.Model):

    activo = models.BooleanField(default=False)
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE)


class Trabajador(models.Model):

    activo = models.BooleanField(default=False)
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE)


class Docente(models.Model):

    activo = models.BooleanField(default=False)
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE)

    class Meta:
        ordering = ('funcionario',)

    def __str__(self):
        return str(self.funcionario)

class Vacaciones(models.Model):

    activo = models.BooleanField(default=True)
    dias_pendientes = models.PositiveSmallIntegerField()
    dias_totales = models.PositiveSmallIntegerField()
    funcionario = models.ForeignKey('talento_humano.Funcionario', on_delete=models.CASCADE)
    horas_pendientes = models.PositiveSmallIntegerField(default=0)
    horas_totales = models.PositiveSmallIntegerField(default=0)
    minutos_pendientes = models.PositiveSmallIntegerField(default=0)
    minutos_totales = models.PositiveSmallIntegerField(default=0)
    periodo_vacaciones = models.ForeignKey('core.PeriodoVacaciones', on_delete=models.PROTECT)
    asignacion_puesto = models.ForeignKey('talento_humano.AsignacionPuesto', default=None, on_delete=models.CASCADE)

    class Meta:
        ordering = ['funcionario', ]

    @staticmethod
    def buscar(criterio):
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            print(p_criterio)
            for i in p_criterio:
                print("qset", qset)
                qset = qset & (Q(funcionario__usuario__persona__primer_apellido__icontains=i) | Q(
                    funcionario__usuario__persona__segundo_apellido__icontains=i) | Q(
                    funcionario__usuario__persona__primer_nombre__icontains=i) | Q(
                    funcionario__usuario__persona__segundo_nombre__icontains=i) | Q(
                    funcionario__usuario__persona__numero_documento__icontains=i)
                               )
                print(qset)
        return Vacaciones.objects.filter(qset).distinct()

    @staticmethod
    @app.task
    def generar_vacaciones():
        """
        Genera el tiempo de vacaciones el cual el funcionario tiene derecho en un periodo fiscal
        variable: representa el número de dias por meses que se tiene derecho a vacaciones de acuerdo al 
        límite de los días por  ejemplo si al año tiene derecho a 30 dias de vacación entonces 30/12=2.5 dias por mes 
        :return:
        """
        i = 0
        for funcionario in Funcionario.get_funcionarios_activos(vigente=True).all():
            i += 1

            """
            puestoReciente= None
            aux = None
            aux2 = None
            num =1
            for p in funcionario.asignaciones_puestos.all():
                print('         /-------------**********************************')
                print('         id'+str(p.id))
                print("         vigente "+str(p.vigente))
                print("         fecha inicio "+str(p.fecha_inicio))
                print("         fecha fin "+str(p.fecha_fin))
                print('         puesto '+str(p.uaa_puesto.puesto))
                print('         activo '+str(p.activo))
                print('         vacaciones '+str())
                print('         /-------------**********************************')
            print("resultado del auxiliar obtenido  "+ str(aux))
            """

            if funcionario.es_funcionario_activo():
                periodo_vacaciones = funcionario.get_periodo_vacaciones(activo=True)
                """
                c=CompensacionDias.objects.filter().all()
                print('**************************-----------')
                for f in c:
                    print (f)
                print('**************************-----------')

                r =  RegistroVacaciones.objects.filter().all()
                print('**************************-----------')
                for f in r:
                    print (f.fecha_inicio)
                    print(f.fecha_fin)
                print('**************************-----------')

                v = Vacaciones.objects.filter().all()
                print('**************************-----------')

                m =0
                for f in v:
                    print (f.dias_pendientes)
                    print(f.dias_totales)
                    m+=1
                    if m==5:
                        break
                    print('               **************************-----------')
                print('**************************-----------')
                """
                if not funcionario.tiene_vacacion():
                    asignacion_puesto = funcionario.get_asignacion_puesto_vigente()
                    dias_limite = asignacion_puesto.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.vacaciones
                    variable = dias_limite / 12
                    periodo_vacaciones = funcionario.get_periodo_vacaciones(activo=True)
                    if periodo_vacaciones:
                        # JJM 2019-01-31
                        fecha_inicial = fecha.fecha_mayor(asignacion_puesto.fecha_inicio,
                                                          periodo_vacaciones.fecha_inicio)
                        fecha_final = fecha.fecha_menor(asignacion_puesto.fecha_termino,
                                                        asignacion_puesto.fecha_fin)
                        fecha_final = fecha.fecha_menor(fecha_final, periodo_vacaciones.fecha_fin)
                        fecha_final = fecha_final + datetime.timedelta(days=1)
                        tiempo_total = fecha.diferencia(fecha_inicial, fecha_final)
                        dias = (tiempo_total['anios'] * 12 + tiempo_total[
                            'meses']) * variable  # obtengo años en meses  y * variable
                        dias = dias + tiempo_total['dias'] / 100 * variable
                        # dias = asignacion_puesto.get_meses_laborados(periodo_vacaciones) * variable
                        # dias = dias + asignacion_puesto.get_dias_laborados(periodo_vacaciones) / 100 * variable
                        horas = abs(dias) - abs(int(dias))
                        horas = horas * 8
                        vacaciones = Vacaciones(activo=True, funcionario=funcionario,
                                                asignacion_puesto=asignacion_puesto,
                                                periodo_vacaciones=periodo_vacaciones,
                                                dias_totales=dias, dias_pendientes=dias, horas_totales=horas,
                                                horas_pendientes=horas)
                        vacaciones.save()

                        # demf: Genera compensación de dias para vacaciones anteriores y nuevas

                        vacacionesAnteriores = Vacaciones.objects.filter(Q(funcionario_id=funcionario.id) & (
                                    Q(dias_pendientes__gt=0) | Q(horas_pendientes__gt=0) | Q(
                                minutos_pendientes__gt=0)) & Q(activo=True))
                        for vacAnterior in vacacionesAnteriores:
                            if vacAnterior.dias_pendientes > 0 or vacAnterior.horas_pendientes > 0 or vacAnterior.minutos_pendientes > 0:
                                # vacAnterior.activo = False
                                compensacionAnt = CompensacionDias(vacaciones=vacAnterior,
                                                                   horas=vacAnterior.horas_pendientes * -1,
                                                                   dias=vacAnterior.dias_pendientes * -1,
                                                                   minutos=vacAnterior.minutos_pendientes * -1,
                                                                   observacion='Vacaciones pendientes a: ' + vacaciones.periodo_vacaciones.nombre)

                                compensacionNew = CompensacionDias(vacaciones=vacaciones,
                                                                   horas=vacAnterior.horas_pendientes,
                                                                   dias=vacAnterior.dias_pendientes,
                                                                   minutos=vacAnterior.minutos_pendientes,
                                                                   observacion='Vacaciones pendientes de: ' + vacAnterior.periodo_vacaciones.nombre)

                                compensacionAnt.save()
                                compensacionNew.save()
                                vacAnterior.recalcular_dias_pendientes()
                                vacAnterior.activo = False
                                vacAnterior.save()

                        vacaciones.recalcular_dias_pendientes()
            # if i == 200:
            #     break

        return

    @staticmethod
    def get_vacaciones(funcionario, periodo_vacaciones):
        if not isinstance(funcionario, Funcionario):
            return None
        if not isinstance(periodo_vacaciones, PeriodoVacaciones):
            return None
        return Vacaciones.objects.filter(funcionario=funcionario, periodo_vacaciones=periodo_vacaciones).first()

    def recalcular_dias_pendientes(self):
        cont = 0
        dias_compensacion = 0
        horas_compensacion = 0
        minutos_compensacion = 0

        dias_ausentismos = 0
        horas_ausentismo = 0
        minutos_ausentismo = 0

        self.horas_pendientes = self.horas_totales
        self.minutos_pendientes = 0
        for registro in self.registrovacaciones_set.all():
            cont = cont + registro.get_numero_dias()
        for ausentismo in self.ausentismofuncionario_set.all():
            # cont = cont + ausentismo.get_numero_dias()
            dias_ausentismos = dias_ausentismos + ausentismo.dias
            horas_ausentismo = horas_ausentismo + ausentismo.horas
            minutos_ausentismo = minutos_ausentismo + ausentismo.minutos

        for compensacion in self.compensaciondias_set.all():
            dias_compensacion = dias_compensacion + compensacion.dias
            horas_compensacion = horas_compensacion + compensacion.horas
            minutos_compensacion = minutos_compensacion + compensacion.minutos
        self.dias_pendientes = self.dias_totales - cont + dias_compensacion - dias_ausentismos
        self.horas_pendientes = self.horas_pendientes + horas_compensacion - horas_ausentismo
        self.minutos_pendientes = self.minutos_pendientes + minutos_compensacion - minutos_ausentismo
        while self.minutos_pendientes > 59:
            self.minutos_pendientes = 60 - self.minutos_pendientes
            self.horas_pendientes = self.horas_pendientes + 1

        while self.horas_pendientes > 8:
            self.horas_pendientes = 8 - self.horas_pendientes
            self.dias_pendientes = self.dias_pendientes + 1

        while self.minutos_pendientes < 0:
            self.horas_pendientes = self.horas_pendientes - 1
            self.minutos_pendientes = 60 - abs(self.minutos_pendientes)

        while self.horas_pendientes < 0:
            self.dias_pendientes = self.dias_pendientes - 1
            self.horas_pendientes = 8 - abs(self.horas_pendientes)
        self.dias_pendientes = self.dias_pendientes if self.dias_pendientes > 0 else 0
        self.save()
        return

    def recalcular_vacaciones(self):
        asignacion_puesto = self.asignacion_puesto
        periodo_vacaciones = self.periodo_vacaciones
        dias_limite = asignacion_puesto.uaa_puesto.puesto.grupo_ocupacional.regimen_laboral.vacaciones
        variable = dias_limite / 12
        if periodo_vacaciones:
            fecha_inicial = fecha.fecha_mayor(asignacion_puesto.fecha_inicio, periodo_vacaciones.fecha_inicio)
            fecha_final = fecha.fecha_menor(asignacion_puesto.fecha_termino, asignacion_puesto.fecha_fin)
            fecha_final = fecha.fecha_menor(fecha_final, periodo_vacaciones.fecha_fin)
            # sumo un dia para que fecha final sea inclusiva en la clase FechaUtil
            fecha_final = fecha_final + datetime.timedelta(days=1)
            tiempo_total = fecha.diferencia(fecha_inicial, fecha_final)
            dias = (tiempo_total['anios'] * 12 + tiempo_total[
                'meses']) * variable  # obtengo años en meses  y * variable
            dias = dias + tiempo_total['dias'] / 100 * variable
            horas = abs(dias) - abs(int(dias))
            horas = horas * 8
            self.dias_totales = dias
            self.horas_totales = horas
            self.save()
            self.recalcular_dias_pendientes()

    def reducir_dias_vacaciones(self, dias=0):
        self.dias_pendientes = self.dias_pendientes - dias
        self.save()
        return

    @staticmethod
    def reporte_vacaciones_pendientes():
        qset = (Q(activo=True) & (Q(dias_pendientes__gt=0) | Q(horas_pendientes__gt=0) | Q(minutos_pendientes__gt=0)))
        qset = qset & Q(funcionario__activo=True)
        consulta = Vacaciones.objects.filter(qset).order_by(
            'funcionario__usuario__persona__primer_apellido',
            'funcionario__usuario__persona__segundo_apellido',
            'funcionario__usuario__persona__primer_nombre',
            'funcionario__usuario__persona__segundo_nombre'
        )
        return consulta

    @staticmethod
    def reporte_vacaciones_pendientes_busqueda(activo=None, dias_pendientes=None):
        if activo == None:
            activo = True
        qset = (Q(activo=True) & Q(dias_pendientes__gte=dias_pendientes))
        qset = qset & Q(funcionario__activo=activo)
        consulta = Vacaciones.objects.filter(qset).order_by(
            'funcionario__usuario__persona__primer_apellido',
            'funcionario__usuario__persona__segundo_apellido',
            'funcionario__usuario__persona__primer_nombre',
            'funcionario__usuario__persona__segundo_nombre'
        )
        return consulta


class RegistroVacaciones(models.Model):
    """
    Registro de cada uno de los perioodos vacacionales del funcionario
    """
    activo = models.BooleanField(default=True)
    fecha_fin = models.DateTimeField()
    fecha_inicio = models.DateTimeField()
    vacaciones = models.ForeignKey('talento_humano.Vacaciones', on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True)
    detalle_planificacion = models.ForeignKey('configuracion.DetallePlanificacion', on_delete=models.PROTECT)

    class Meta:
        ordering = ['fecha_inicio', 'fecha_fin']

    def generar_vacacion_detalle_planificacion(self, detalle_planificacion):
        if detalle_planificacion is None:
            return None
        if self.se_puede_generar_vacaciones(detalle_planificacion.fecha_desde, detalle_planificacion.fecha_hasta):
            today = datetime.datetime(year=detalle_planificacion.fecha_desde.year,
                                      month=detalle_planificacion.fecha_desde.month,
                                      day=detalle_planificacion.fecha_desde.day)

            if self.vacaciones.dias_pendientes >= detalle_planificacion.get_numero_dias():
                self.activo = True
                self.fecha_inicio = today
                self.fecha_fin = today + datetime.timedelta(days=detalle_planificacion.get_numero_dias() - 1, hours=23,
                                                            minutes=59, seconds=59)
                self.observacion = detalle_planificacion.descripcion
                self.detalle_planificacion = detalle_planificacion
                self.save()
                self.vacaciones.reducir_dias_vacaciones(detalle_planificacion.get_numero_dias())
                return True
            elif self.vacaciones.dias_pendientes > 0:
                self.activo = True
                self.fecha_inicio = today
                self.fecha_fin = today + datetime.timedelta(days=self.vacaciones.dias_pendientes - 1, hours=23,
                                                            minutes=59, seconds=59)
                self.observacion = detalle_planificacion.descripcion
                self.detalle_planificacion = detalle_planificacion
                self.save()
                self.vacaciones.reducir_dias_vacaciones(self.vacaciones.dias_pendientes)
                return True
        else:
            print('no se puede generar vacaciones, ya existe')
        return None

    def get_numero_dias(self):
        diferencia = self.fecha_fin - self.fecha_inicio
        return diferencia.days + 1

    def se_puede_generar_vacaciones(self, fecha_desde, fecha_hasta):
        if fecha_desde and fecha_hasta:
            qset = (Q(fecha_inicio__gte=fecha_desde) & Q(fecha_inicio__lte=fecha_hasta))
            qset = qset | (Q(fecha_fin__gte=fecha_desde) & Q(fecha_fin__lte=fecha_hasta))
            qset = qset | (Q(fecha_inicio__lt=fecha_desde) & Q(fecha_fin__gt=fecha_hasta))
            qset = qset & (Q(vacaciones__funcionario=self.vacaciones.funcionario))
            consulta = RegistroVacaciones.objects.filter(qset)
            print(self.vacaciones.funcionario.id)
            return consulta.count() == 0
        else:
            return None

    @staticmethod
    def reporte_vacaciones_detalle(detalle_planificacion=None):
        qset = (~Q(detalle_planificacion=None))
        if detalle_planificacion:
            qset = qset & Q(detalle_planificacion=detalle_planificacion)
        consulta = RegistroVacaciones.objects.filter(qset).order_by(
            'vacaciones__funcionario__usuario__persona__primer_apellido',
            'vacaciones__funcionario__usuario__persona__segundo_apellido',
            'vacaciones__funcionario__usuario__persona__primer_nombre',
            'vacaciones__funcionario__usuario__persona__segundo_nombre'
        )
        return consulta

    @staticmethod
    def reporte_vacaciones_detalle_facultad(detalle_planificacion=None, uaas_ids_facultad=[]):
        qset = (~Q(detalle_planificacion=None) & Q(
            vacaciones__asignacion_puesto__uaa_puesto__uaa_id__in=(uaas_ids_facultad)))
        if detalle_planificacion:
            qset = qset & Q(detalle_planificacion=detalle_planificacion)

        consulta = RegistroVacaciones.objects.filter(qset).order_by(
            'vacaciones__funcionario__usuario__persona__primer_apellido',
            'vacaciones__funcionario__usuario__persona__segundo_apellido',
            'vacaciones__funcionario__usuario__persona__primer_nombre',
            'vacaciones__funcionario__usuario__persona__segundo_nombre'
        )
        return consulta

    @staticmethod
    def reporte_vacaciones_detalle_excludefacultad(detalle_planificacion=None, uaas_ids_facultad=[]):
        qset = (~Q(detalle_planificacion=None) & ~Q(
            vacaciones__asignacion_puesto__uaa_puesto__uaa_id__in=(uaas_ids_facultad)))
        if detalle_planificacion:
            qset = qset & Q(detalle_planificacion=detalle_planificacion)

        consulta = RegistroVacaciones.objects.filter(qset).order_by(
            'vacaciones__asignacion_puesto__uaa_puesto__uaa__nombre',
            'vacaciones__funcionario__usuario__persona__primer_apellido',
            'vacaciones__funcionario__usuario__persona__segundo_apellido',
            'vacaciones__funcionario__usuario__persona__primer_nombre',
            'vacaciones__funcionario__usuario__persona__segundo_nombre'
        )
        return consulta


class CompensacionDias(models.Model):
    """
    Registro de los dias a recuperar si es un valor negativo el funcionario son los dias que debe
    """
    dias = models.IntegerField(default=0, null=True)
    horas = models.IntegerField(default=0, null=True)
    minutos = models.IntegerField(default=0, null=True)
    fecha_registro = models.DateTimeField(auto_now=True)
    observacion = models.TextField(blank=True, null=True)
    vacaciones = models.ForeignKey('talento_humano.Vacaciones', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.observacion)

    def recalcular(self):
        while self.minutos > 59:
            self.minutos = self.minutos - 60
            self.horas = self.horas + 1
        while self.horas > 8:
            self.horas = self.horas - 8
            self.dias = self.dias + 1
        return


class Ausentismo(models.Model):
    """
    Configuración de los permisos licencias y comisiones de servicios vigentes de acuerdo a la LOSEp
    """
    activo = models.BooleanField(default=True)
    acumulable = models.BooleanField(default=False)
    con_remuneracion = models.BooleanField(default=False)
    descuento_sueldo = models.BooleanField(default=False)
    descripcion = models.TextField()
    imputable_vacaciones = models.BooleanField(default=False)
    limite_tiempo = models.BooleanField(default=True)
    limite_anios = models.PositiveSmallIntegerField(blank=True, null=True)
    limite_dias = models.PositiveSmallIntegerField(blank=True, null=True)
    limite_horas = models.PositiveSmallIntegerField(blank=True, null=True)
    limite_meses = models.PositiveSmallIntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=250)
    tipo_ausentismo = models.ForeignKey('core.CatalogoItem',
                                        related_name='tipo_ausentismo',
                                        limit_choices_to={'catalogo__codigo': 'AUSENTISMO'},
                                        on_delete=models.PROTECT)

    class Meta:
        ordering = ['nombre', 'tipo_ausentismo']


class AusentismoFuncionario(models.Model):
    """
    Registro de los ausentismos de cada uno de los funcionarios
    """
    activo = models.BooleanField(default=True)
    ausentismo = models.ForeignKey('talento_humano.Ausentismo', on_delete=models.PROTECT)
    dias = models.IntegerField(default=0, null=True)
    horas = models.IntegerField(default=0, null=True)
    minutos = models.IntegerField(default=0, null=True)
    fecha_fin = models.DateTimeField()
    fecha_inicio = models.DateTimeField()
    fecha_registro = models.DateField(auto_now=True)
    funcionario = models.ForeignKey('talento_humano.Funcionario', on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True)
    vacaciones = models.ForeignKey('talento_humano.Vacaciones', blank=True, null=True, on_delete=models.SET_NULL)
    tipo_permiso = models.ForeignKey('core.CatalogoItem',
                                     related_name='tipo_permiso',
                                     limit_choices_to={'catalogo__codigo': 'TIPO_PERMISO'},
                                     on_delete = models.PROTECT)

    def cumple_limite(self, anio=0, meses=0, dias=0):
        """
        Verifica si cumple el límite de tiempo para el ausentismo
        :param anio: Máximo número de años de ausentismo
        :param meses: Máximo número de meses de ausentismo
        :param dias: Máximo número de dias de ausentismo
        :return:
        """

        # Inicializa
        if anio is None:
            anio = 0
        if meses is None:
            meses = 0
        if dias is None:
            dias = 0
        if meses > 12:
            anio = anio + meses // 12
            meses = meses % 12

        # Dias a decrementar para validar la fecha límite (Se decrementa un día porque el día inicial también cuenta)
        dias_delta = 0
        if anio > 0 or meses > 0 or dias > 0:
            dias_delta = dias - 1;

        anio = self.fecha_inicio.year + anio
        meses = self.fecha_inicio.month + meses
        if meses > 12:
            anio = anio + meses // 12
            meses = meses % 12

        fechaLim = datetime.datetime(year=anio, month=meses, day=1)
        fechaLim = fechaLim + datetime.timedelta(days=self.fecha_inicio.day - 1)
        fechaFin = datetime.datetime(year=self.fecha_fin.year, month=self.fecha_fin.month, day=self.fecha_fin.day)
        fechaLim = fechaLim + datetime.timedelta(days=dias_delta)

        print("fLim: %s, fFin: %s, fLim>=fFin: %s" % (fechaLim, fechaFin, fechaLim >= fechaFin))

        return fechaLim >= fechaFin

    def get_numero_anios(self):
        """
        devuelve el número de años entre las fechas
        :return: número de años
        """
        if not self.fecha_inicio:
            return None
        fecha_desde = self.fecha_inicio.year
        fecha_hasta = self.fecha_fin.year
        if self.fecha_fin.month > self.fecha_inicio.month:
            return fecha_hasta - fecha_desde
        else:
            if self.fecha_fin.month == self.fecha_inicio.month:
                if self.fecha_fin.day >= self.fecha_inicio.day:
                    return fecha_hasta - fecha_desde
                else:
                    return fecha_hasta - fecha_desde - 1
            else:
                return fecha_hasta - fecha_desde - 1

    def get_numero_dias(self):
        """
        Devuelve el número de dias entre estas dos fechas
        :return:
        """
        # diferencia = self.fecha_fin - self.fecha_inicio
        # return diferencia.days + 1
        return self.dias

    def get_total_ausentismo(self):

        horas_dias = self.horas * 0.0417;
        minutos_dias = self.minutos * 0.000694;
        return self.dias + horas_dias + minutos_dias;

    def get_numero_meses(self):
        mes_inicio = self.fecha_inicio.month
        mes_fin = self.fecha_fin.month
        meses = 0
        if self.fecha_inicio.year != self.fecha_fin.year:
            meses = self.get_numero_anios() * 12
        if mes_fin >= mes_inicio:
            meses = meses + mes_fin - mes_inicio
        return meses

    def se_puede_generar_licencia(self, fecha_desde=None, fecha_hasta=None):
        if fecha_desde is None:
            fecha_desde = self.fecha_inicio
        if fecha_hasta is None:
            fecha_hasta = self.fecha_fin
        if fecha_desde and fecha_hasta:
            qset = (Q(fecha_inicio__lte=fecha_desde) & Q(fecha_fin__gte=fecha_desde))
            qset = qset | (Q(fecha_inicio__gte=fecha_hasta) & Q(fecha_fin__lte=fecha_hasta))
            qset = qset & (Q(funcionario=self.funcionario))
            consulta = AusentismoFuncionario.objects.filter(qset)
            return consulta.count() == 0
        else:
            return None
