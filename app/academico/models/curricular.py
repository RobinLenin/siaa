from django.core.exceptions import ValidationError
from django.db import models

REGIMEN_2013 = "2013"
CHOICE_REGIMEN = ((REGIMEN_2013, "2013"),)

class Asignatura(models.Model):
    TIPO_CURSO_APOYO = "CURSO_APOYO"
    TIPO_PROGRAMA_ESTUDIO = "PROGRAMA_ESTUDIO"
    CHOICE_TIPO = ((TIPO_CURSO_APOYO, "Curso de apoyo"),
                   (TIPO_PROGRAMA_ESTUDIO, "Programa de estudio"),)

    codigo_institucional = models.CharField(max_length=25, unique=True)
    codigo_unesco = models.CharField(max_length=25, unique=True)
    nombre = models.TextField()
    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_PROGRAMA_ESTUDIO)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class AsignaturaNivel(models.Model):
    TIPO_OBLIGATORIA = "OBLIGATORIA"
    TIPO_OPTATIVA = "OPTATIVA"
    CHOICE_TIPO = ((TIPO_OBLIGATORIA, "Obligatoria"),
                   (TIPO_OPTATIVA, "Optativa"),)

    duracion = models.PositiveSmallIntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_OBLIGATORIA)

    asignatura = models.ForeignKey('Asignatura', related_name="asignaturas_nivel", on_delete=models.CASCADE)
    campo_formacion = models.ForeignKey('CampoFormacion', on_delete=models.PROTECT, null=True, blank=True)
    correquisitos = models.ManyToManyField('self', related_name="correquisito", blank=True)
    nivel = models.ForeignKey('Nivel', on_delete=models.CASCADE, related_name="asignaturas")
    prerrequisitos = models.ManyToManyField('self', related_name="postrrequisito", blank=True, symmetrical=False)

    class Meta:
        verbose_name_plural = 'Asignaturas de nivel'

    def __str__(self):
        return self.asignatura.nombre

    def actualizar_duracion(self):
        """
        Actualiza la duración de la asignatura nivel de acuerdo a la sumatoria de las asignaturas componentes
        :return:
        """
        self.duracion = self.asignaturas_componente.aggregate(total=models.Sum('duracion')).get('total') or 0
        self.save()


    def get_correquisitos_ids(self):
        """
        Retorna los ids de los correquisitos de la asignatura nivel
        :return:
        """
        return self.correquisitos.values_list('id', flat=True)


    def get_prerrequisitos_ids(self):
        """
        Retorna los ids de los prerrequisitos de la asignatura nivel
        :return:
        """
        return self.prerrequisitos.values_list('id', flat=True)


    def validate_unique(self, *args, **kwargs):
        """
        Valida que la asignatura sea asignada al pensum una sola vez
        :param args:
        :param kwargs:
        :return:
        """
        super(AsignaturaNivel, self).validate_unique(*args, **kwargs)
        asignatura = self.__class__.objects.filter(asignatura=self.asignatura, nivel__pensum=self.nivel.pensum).exclude(
            id=self.id)
        if asignatura.exists():
            raise ValidationError(
                message='Error, la asignatura ya está agregada en el pensum: Nivel: %s' % asignatura.first().nivel,
                code='unique_together',
            )


class AsignaturaComponente(models.Model):
    duracion = models.PositiveSmallIntegerField()

    asignatura_nivel = models.ForeignKey('AsignaturaNivel', on_delete=models.CASCADE,
                                         related_name='asignaturas_componente')
    componente_aprendizaje = models.ForeignKey('ComponenteAprendizaje', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Componente de asignatura'
        verbose_name_plural = 'Componentes de asignatura'

    def save(self, *args, **kwargs):
        """
        Al guardar un registro, actualiza la duración total de la asignatura nivel
        :param args:
        :param kwargs:
        :return:
        """
        super(AsignaturaComponente, self).save(*args, **kwargs)
        self.asignatura_nivel.actualizar_duracion()

class Autoridad(models.Model):
    activo = models.BooleanField(default=False)
    abreviatura = models.CharField(max_length=25)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    funcionario = models.ForeignKey('talento_humano.Funcionario', on_delete=models.PROTECT)
    referencia_ingreso = models.TextField(max_length=250)
    referencia_salida = models.TextField(null=True, blank=True, max_length=250)

    class Meta:
        ordering = ['-activo', 'fecha_inicio']


class AutoridadFacultad(Autoridad):
    TIPO_DECANO = "DECANO"
    TIPO_SECRETARIO_ABOGADO = "SECRETARIO_ABOGADO"
    CHOICE_TIPO = ((TIPO_DECANO, "Decano(a)"),
                   (TIPO_SECRETARIO_ABOGADO, "Secretario(a) abogado(a)"),)

    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_SECRETARIO_ABOGADO)

    facultad = models.ForeignKey('Facultad', on_delete=models.CASCADE, related_name='autoridades_facultad')

    class Meta:
        ordering = ['-activo', 'tipo', 'fecha_inicio']
        verbose_name = 'Autoridad de facultad'
        verbose_name_plural = 'Autoridades de facultad'

    def __str__(self):
        return "%s %s" % (self.funcionario, self.tipo)


class AutoridadProgramaEstudio(Autoridad):
    TIPO_DIRECTOR = "DIRECTOR"
    TIPO_GESTOR = "GESTOR "
    TIPO_SECRETARIO = "SECRETARIO"
    CHOICE_TIPO = ((TIPO_DIRECTOR, "Director(a)"),
                   (TIPO_GESTOR, "Gestor(a)"), (TIPO_SECRETARIO, "Secretario(a)"),)
    NUMERO_ACTIVOS = {TIPO_DIRECTOR: 1, TIPO_GESTOR: 1, TIPO_SECRETARIO: 2}

    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_SECRETARIO)

    programa_estudio = models.ForeignKey('ProgramaEstudio', on_delete=models.CASCADE,
                                         related_name='autoridades_programa_estudio')

    class Meta:
        ordering = ['-activo', 'tipo', 'fecha_inicio']
        verbose_name = 'Autoridad de programa de estudio'
        verbose_name_plural = 'Autoridades de programa de estudio'

    def __str__(self):
        return "%s %s" % (self.funcionario, self.tipo)


class CampoFormacion(models.Model):
    nombre = models.TextField()

    nivel_formacion = models.ForeignKey('NivelFormacion', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Campo de formación'
        verbose_name_plural = 'Campos de formación'
        ordering = ['nivel_formacion__regimen']

    def __str__(self):
        return '%s - %s' % (self.nivel_formacion, self.nombre)


class ComponenteAprendizaje(models.Model):
    codigo = models.CharField(max_length=25)
    nombre = models.CharField(max_length=100)
    regimen = models.CharField(max_length=25, choices=CHOICE_REGIMEN, default=REGIMEN_2013)

    class Meta:
        ordering = ['regimen', 'nombre']
        verbose_name = 'Componente de aprendizaje'
        verbose_name_plural = 'Componentes de aprendizaje'

    def __str__(self):
        return self.nombre


class Facultad(models.Model):
    nombre = models.TextField()
    siglas = models.CharField(max_length=25)

    class Meta:
        verbose_name_plural = 'Facultades'

    def __str__(self):
        return self.nombre


class NivelFormacion(models.Model):
    ESTADO_ACTIVO = "ACTIVO"
    CHOICE_ESTADO = ((ESTADO_ACTIVO, "Activo"),)

    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=25, choices=CHOICE_ESTADO, default=ESTADO_ACTIVO)
    nombre = models.TextField()
    regimen = models.CharField(max_length=25, choices=CHOICE_REGIMEN, default=REGIMEN_2013)

    class Meta:
        verbose_name = 'Nivel de formación'
        verbose_name_plural = 'Niveles de formación'

    def __str__(self):
        return '%s (%s)' % (self.nombre, self.get_regimen_display())


class Nivel(models.Model):
    numero = models.PositiveSmallIntegerField()

    organizacion_curricular = models.ForeignKey('OrganizacionCurricular', on_delete=models.PROTECT, null=True, blank=True)
    pensum = models.ForeignKey('Pensum', on_delete=models.CASCADE, related_name='niveles')

    class Meta:
        ordering = ['pensum__id', 'numero']
        unique_together = ('numero', 'pensum')
        permissions = (('add_asignaturanivel', 'Puede agregar asignaturas al nivel'),)
        verbose_name_plural = 'Niveles'

    def __str__(self):
        return str(self.numero)

    def get_prerrequisitos_posibles(self, asignatura_nivel=None):
        """
        Permite obtener los prerequisitos posibles de un nivel del pensum
        :param asignatura_nivel: Si viene se excluye los prerequisitos ya establecidos
        :return:
        """
        prerrequisitos = AsignaturaNivel.objects.filter(nivel__pensum=self.pensum, nivel__numero__lt=self.numero)
        if asignatura_nivel:
            prerrequisitos = prerrequisitos.exclude(id__in=asignatura_nivel.get_prerrequisitos_ids())
        return prerrequisitos


class OrganizacionCurricular(models.Model):
    nombre = models.TextField()

    nivel_formacion = models.ForeignKey('NivelFormacion', on_delete=models.CASCADE)

    class Meta:
        ordering = ['nivel_formacion__regimen']
        verbose_name_plural = 'Organizaciones curriculares'

    def __str__(self):
        return self.nombre


class Pensum(models.Model):
    DURACION_UNIDAD_CREDITO = "CREDITO"
    DURACION_UNIDAD_HORA = "HORA"
    CHOICE_DURACION_UNIDAD = ((DURACION_UNIDAD_CREDITO, "Crédito"), (DURACION_UNIDAD_HORA, "Hora"),)

    ORGANIZACION_CICLO = "CICLO"
    CHOICE_ORGANIZACION = ((ORGANIZACION_CICLO, "Ciclo"),)

    TIPO_COMPONENTE = "COMPONENTE"
    CHOICE_TIPO = ((TIPO_COMPONENTE, "Por componentes"),)

    duracion_unidad = models.CharField(max_length=25, choices=CHOICE_DURACION_UNIDAD, default=DURACION_UNIDAD_HORA)
    editable = models.BooleanField(default=False)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    nombre = models.TextField()
    organizacion = models.CharField(max_length=25, choices=CHOICE_ORGANIZACION, default=ORGANIZACION_CICLO)
    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_COMPONENTE)

    programa_estudio = models.ForeignKey('ProgramaEstudio', on_delete=models.CASCADE, related_name='pensums')
    pensums_grupo = models.ManyToManyField('PensumGrupo', blank=True)

    class Meta:
        ordering = ['editable', 'fecha_inicio']
        unique_together = ('programa_estudio','nombre',)
        permissions = (('add_nivel', 'Puede agregar niveles al pensum'),)

    def __str__(self):
        return self.nombre

    def __init__(self, *args, **kwargs):
        super(Pensum, self).__init__(*args, **kwargs)
        self.__original_editable = self.editable

    def get_pensums_grupo_ids(self):
        """
        Retorna la lista de ids de los pensum groups asociados al pensum
        :return:
        """
        return self.pensums_grupo.values_list('id', flat=True)


class PensumComplementario(models.Model):
    """
    Modelo que permite definir un pensum, que será complemento para aprobar una carrera
    Ejm: El pensum de Cultura Fisica puede ser complemento de muchos otros  pensum de carreras
    La relación se completa mediante el modelo PensumGrupo
    """

    TIPO_OBLIGATORIO = "OBLIGATORIO"
    TIPO_OPTATIVO = "OPTATIVO"
    CHOICE_TIPO = ((TIPO_OBLIGATORIO, "Obligatorio"), (TIPO_OPTATIVO, "Optativo"),)

    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_OBLIGATORIO)

    pensum = models.ForeignKey('Pensum', on_delete=models.PROTECT, related_name='pensums_complementarios')
    pensum_grupo = models.ForeignKey('PensumGrupo', on_delete=models.CASCADE, related_name='pensums_complementarios')

    class Meta:
        ordering = ['tipo']
        unique_together = ('pensum', 'pensum_grupo')
        verbose_name_plural = 'Pensums complementarios'

    def __str__(self):
        return self.pensum


class PensumGrupo(models.Model):
    """
    Modelo que expresa un grupo de pensums que son de caracter obligatorio u optativo
    Va  a permitir agrupar pensums comunes
    Ejm Pensums del Curso de Computación presencial y Curso Computación Virtual
    """

    nombre = models.CharField(max_length=25)
    nivel_inicio = models.PositiveSmallIntegerField(null=True, blank=True)
    nivel_fin = models.PositiveSmallIntegerField(null=True, blank=True)
    nro_optativo_obligatorios = models.PositiveSmallIntegerField(default=0)
    """ Nro optativos, permite definir cuantos de los pensums optativo van a ser obligatorios
        si cero, el estudiante puede tomar ninguno o todos los pensums """

    class Meta:
        verbose_name = 'Agrupación de Pensum'
        verbose_name_plural = 'Agrupaciones de pensum'

    def __str__(self):
        return self.nombre


class ProgramaEstudio(models.Model):
    ESTADO_ACTIVO = "ACTIVO"
    CHOICE_ESTADO = ((ESTADO_ACTIVO, "Activo"),)

    MODALIDAD_PRESENCIAL = "PRESENCIAL"
    MODALIDAD_DISTANCIA = "DISTANCIA"
    CHOICE_MODALIDAD = ((MODALIDAD_PRESENCIAL, "Presencial"), (MODALIDAD_DISTANCIA, "Distancia"),)

    TIPO_CURSO_APOYO = "CURSO_APOYO"
    TIPO_PROGRAMA_ESTUDIO = "PROGRAMA_ESTUDIO"
    CHOICE_TIPO = ((TIPO_CURSO_APOYO, "Curso de apoyo"), (TIPO_PROGRAMA_ESTUDIO, "Programa de estudio"),)

    codigo_institucional = models.CharField(max_length=25, unique=True)
    codigo_senescyt = models.CharField(max_length=25, unique=True)
    estado = models.CharField(max_length=25, choices=CHOICE_ESTADO, default=ESTADO_ACTIVO)
    fecha_creacion = models.DateField()
    fecha_aprobacion = models.DateField()
    fecha_culminacion = models.DateField(null=True, blank=True)
    modalidad = models.CharField(max_length=25, choices=CHOICE_MODALIDAD, default=MODALIDAD_PRESENCIAL)
    nombre = models.TextField()
    regimen = models.CharField(max_length=25, choices=CHOICE_REGIMEN, default=REGIMEN_2013)
    tipo = models.CharField(max_length=25, choices=CHOICE_TIPO, default=TIPO_PROGRAMA_ESTUDIO)

    campo_detallado = models.ForeignKey('CampoDetallado', on_delete=models.PROTECT, null=True, blank=True)
    facultad = models.ForeignKey('Facultad', on_delete=models.CASCADE, related_name='programas_estudio')
    tipo_formacion = models.ForeignKey('TipoFormacion', on_delete=models.PROTECT, null=True, blank=True, related_name="programas_estudio")

    class Meta:
        verbose_name = 'Programa de estudio'
        verbose_name_plural = 'Programas de estudio'

    def __str__(self):
        return self.nombre


    def get_campos_formacion(self):
        """
        Retorna los tipos de formacion de acuerdo al nivel_formacion al que pertenece el programa de estudio
        :return:
        """
        return CampoFormacion.objects.filter(nivel_formacion__tipos_formacion__programas_estudio__id=self.id)


    def get_organizaciones_curriculares(self):
        """
        Retorna las organizaciones curriculares de acuerdo al nivel_formacion al que pertenece el programa de estudio
        :return:
        """
        return OrganizacionCurricular.objects.filter(nivel_formacion__tipos_formacion__programas_estudio__id=self.id)


class Titulo(models.Model):
    activo = models.BooleanField(default=False)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    nombre = models.TextField()

    pensum = models.ForeignKey('Pensum', on_delete=models.CASCADE, related_name='titulos')

    class Meta:
        ordering = ['-activo', '-nombre']
        verbose_name = 'Título'
        verbose_name_plural = 'Títulos'

    def __str__(self):
        return self.nombre


class TipoFormacion(models.Model):
    nombre = models.TextField()

    nivel_formacion = models.ForeignKey('NivelFormacion', on_delete=models.CASCADE, related_name="tipos_formacion")

    class Meta:
        ordering = ['nivel_formacion__regimen']
        verbose_name = 'Tipo de formación'
        verbose_name_plural = 'Tipos de formación'

    def __str__(self):
        return self.nombre
