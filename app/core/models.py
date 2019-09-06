import datetime

from django.db import models
from django.db.models import Q

from app.bsg.views import *
from app.core.utils.fecha import calcular_edad
from app.core.utils.general import dividir_nombres_completos


class Pais(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.PositiveSmallIntegerField(null=True, blank=True)
    codigo2 = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'País'
        verbose_name_plural = 'Paises'

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    nombre = models.CharField(max_length=150)
    codigo_th = models.PositiveSmallIntegerField(null=True)
    codigo_inec = models.CharField(max_length=2, unique=True, null=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Canton(models.Model):
    nombre = models.CharField(max_length=150)
    codigo_th = models.PositiveSmallIntegerField(null=True)
    codigo_inec = models.CharField(max_length=4, unique=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cantón'
        verbose_name_plural = 'Cantones'

    def __str__(self):
        return self.nombre


class Parroquia(models.Model):
    nombre = models.CharField(max_length=150)
    codigo_th = models.PositiveSmallIntegerField(null=True)
    codigo_inec = models.CharField(max_length=6, null=True)
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return '%s(%s-%s-%s)' % (self.nombre,
                                 str(self.canton.nombre),
                                 str(self.canton.provincia.nombre),
                                 str(self.canton.provincia.pais.nombre))


class Catalogo(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(max_length=350)
    version = models.IntegerField()
    activo = models.NullBooleanField(default=True)
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    orden = models.IntegerField(null=True)

    class Meta:
        ordering = ['codigo', ]

    def __str__(self):
        return self.nombre


class CatalogoItem(models.Model):
    catalogo = models.ForeignKey(Catalogo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(null=True)
    codigo_th = models.CharField(max_length=50)
    codigo_sg = models.CharField(blank=True, null=True, max_length=50)
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    activo = models.NullBooleanField(default=True)
    orden = models.IntegerField(null=True)

    class Meta:
        ordering = ['catalogo', 'orden', 'nombre']
        verbose_name = 'Catalogo item'
        verbose_name_plural = 'Catalogos items'

    def __str__(self):
        return self.nombre

    @staticmethod
    def get_catalogos_items(codigo_catalogo):
        """
        Retorna los catalogos items de acuerdo al nombre del catalogo padre
        :param codigo_catalogo:
        :return:
        """
        return CatalogoItem.objects.filter(catalogo__codigo=codigo_catalogo, activo=True).all().order_by('nombre')

    @staticmethod
    def get_catalogo_item(codigo_catalogo, codigo_item):
        """
        Retorna un catalogo item de acuerdo a su codigo th y al nombre del catalogo de su padre
        :param codigo_catalogo:
        :param codigo_item:
        :return:
        """
        return CatalogoItem.objects.filter(catalogo__codigo=codigo_catalogo, codigo_th=codigo_item).first()

    @staticmethod
    def get_catalogo_item_nombre(codigo_catalogo, nombre):
        """
        Retorna un catalogo item de acuerdo a su nombre y al nombre del catalogo de su padre
        :param codigo_catalogo:
        :param nombre:
        :return:
        """
        return CatalogoItem.objects.filter(catalogo__codigo=codigo_catalogo, nombre=nombre).first()


class InsitucionEducativa(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=10, blank=True, null=True)
    tipo_codigo = models.ForeignKey(CatalogoItem,
                                    related_name='intitucion_tipo_codigo',
                                    limit_choices_to={'catalogo__codigo': 'CODIGO_INSTITUCION_EDUCATIVA'},
                                    blank=True,
                                    null=True,
                                    on_delete = models.SET_NULL)
    sostenimiento = models.ForeignKey(CatalogoItem,
                                      related_name='tipo_sostenimiento',
                                      limit_choices_to={'catalogo__codigo': 'TIPO_SOSTENIMIENTO'},
                                      on_delete=models.PROTECT)
    parroquia = models.ForeignKey(Parroquia, blank=True, null=True, on_delete=models.SET_NULL)
    canton = models.ForeignKey(Canton, blank=True, null=True, on_delete=models.SET_NULL)
    nivel_formacion = models.ManyToManyField(CatalogoItem,
                                             related_name='niveles_formacion',
                                             limit_choices_to={'catalogo__codigo': 'NIVEL_FORMACION'})

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Institucion Educativa'
        verbose_name_plural = 'Instituciones Educativas'

    def __str__(self):
        lugar = self.parroquia.canton.nombre if self.parroquia and self.parroquia.canton else ''
        return u'%s-%s' % (str(self.nombre), lugar)


class IES(models.Model):
    nombre = models.CharField(max_length=140)
    siglas = models.CharField(max_length=40)
    tipologia = models.ForeignKey(CatalogoItem,
                                  related_name='tipologia',
                                  limit_choices_to={'catalogo__codigo': 'TIPOLOGIA_INSTITUCION_SUPERIOR'},
                                  on_delete=models.PROTECT)
    codigo = models.CharField(max_length=140)
    base_legal = models.TextField()
    ruc = models.CharField(max_length=15)
    mision = models.TextField()
    vision = models.TextField()

    class Meta:
        verbose_name = "Institución de Educación Superior"
        verbose_name_plural = "Intituciones de Educación Superior"

    def __str__(self):
        return self.nombre


class Sede(models.Model):
    nombre = models.CharField(max_length=140)
    descripcion = models.TextField(blank=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    tipo_sede = models.OneToOneField(CatalogoItem, related_name='tipo_sede',
                                     limit_choices_to={'catalogo__codigo': 'TIPO_SEDE'}, on_delete=models.CASCADE)
    ies = models.ForeignKey('core.IES', on_delete=models.CASCADE)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Campus(models.Model):
    nombre = models.CharField(max_length=140)
    descripcion = models.TextField(blank=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    canton = models.ForeignKey(Canton, on_delete=models.PROTECT)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Campus'

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    tipo_documento = models.ForeignKey(CatalogoItem,
                                       related_name='tipo_documento',
                                       limit_choices_to={'catalogo__codigo': 'TIPO_DOCUMENTO'},
                                       on_delete=models.PROTECT)
    numero_documento = models.CharField(max_length=20, unique=True)
    numero_libreta_militar = models.CharField(max_length=20, blank=True, null=True)
    primer_apellido = models.CharField(max_length=140)
    segundo_apellido = models.CharField(max_length=140, blank=True)
    primer_nombre = models.CharField(max_length=140)
    segundo_nombre = models.CharField(max_length=140, blank=True)
    fecha_nacimiento = models.DateField(null=True)
    condicion_cedulado = models.ForeignKey(CatalogoItem, null=True, blank=True,
                                           related_name='condicion_cedulado',
                                           limit_choices_to={'catalogo__codigo': 'CONDICION_CEDULADO'},
                                           on_delete=models.PROTECT)
    profesion = models.CharField(max_length=30, blank=True, null=True)
    discapacidad = models.BooleanField(default=False, blank=True)
    numero_carnet_conadis = models.CharField(max_length=20, blank=True, null=True)
    porcentaje_discapacidad = models.PositiveIntegerField(null=True, blank=True)
    fecha_registro_conadis = models.DateTimeField(blank=True, null=True)
    tipo_discapacidad = models.ForeignKey(CatalogoItem, null=True, blank=True,
                                          related_name='tipo_discapacidad',
                                          limit_choices_to={'catalogo__codigo': 'TIPO_DISCAPACIDAD'}
                                          , on_delete=models.SET_NULL)
    grado_discapacidad = models.ForeignKey(CatalogoItem, null=True, blank=True,
                                           related_name='grado_discapacidad',
                                           limit_choices_to={'catalogo__codigo': 'GRADO_DISCAPACIDAD'},
                                           on_delete=models.SET_NULL)
    estado_civil = models.ForeignKey(CatalogoItem, null=True,
                                     related_name='estado_civil',
                                     limit_choices_to={'catalogo__codigo': 'ESTADO_CIVIL'},
                                     on_delete=models.PROTECT)
    tipo_sangre = models.ForeignKey(CatalogoItem, blank=True, null=True,
                                    related_name='tipo_sangre',
                                    limit_choices_to={'catalogo__codigo': 'TIPO_SANGRE'},
                                    on_delete=models.PROTECT)
    sexo = models.ForeignKey(CatalogoItem,
                             related_name='sexo',
                             limit_choices_to={'catalogo__codigo': 'TIPO_SEXO'},
                             on_delete=models.PROTECT)
    nacionalidad = models.ForeignKey(CatalogoItem, null=True,
                                     related_name='nacionalidad',
                                     limit_choices_to={'catalogo__codigo': 'NACIONALIDAD'},
                                     on_delete=models.PROTECT)
    anios_residencia = models.PositiveSmallIntegerField(blank=True,
                                                        null=True,
                                                        help_text='Por favor ingrese este dato solo si su Nacionalidad NO es Ecuatoriana')
    tipo_etnia = models.ForeignKey(CatalogoItem, null=True,
                                   related_name='tipo_etnia',
                                   limit_choices_to={'catalogo__codigo': 'TIPO_ETNIA'},
                                   on_delete=models.PROTECT)
    nacionalidad_indigena = models.ForeignKey(CatalogoItem, blank=True, null=True,
                                              related_name='nacionalidad_indigena',
                                              limit_choices_to={'catalogo__codigo': 'NACIONALIDAD_INDIGENA'},
                                              on_delete=models.PROTECT)

    correo_electronico = models.EmailField(null=True, blank=True)
    correo_electronico_alternativo = models.EmailField(blank=True, null=True)
    validado_bsg = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ['primer_apellido', 'segundo_apellido']

    def __str__(self):
        return self.get_nombres_completos_inverso()

    def get_direccion_domicilio(self):
        """
        Retorna la dirección de domicilio
        :return:
        """
        direcciones = [d for d in self.direccion_set.all() if d.tipo_direccion.nombre == u'Domicilio']
        return direcciones[0] if direcciones else None

    def get_edad(self):
        """
        Calcula y retorna la edad
        :return:
        """
        return calcular_edad(self.fecha_nacimiento)

    def get_foto_url(self):
        """
        Retorna la foto asociado al usuario
        :return:
        """
        if hasattr(self, 'usuario'):
            return self.usuario.foto_url
        return None

    def get_apellidos(self):
        """
        Retorna los apellidos completos
        :return:
        """
        return self.primer_apellido + ' ' + self.segundo_apellido

    def get_nombres(self):
        """
        Retorna los nombres completos
        :return:
        """
        return self.primer_nombre + ' ' + self.segundo_nombre

    def get_nombres_completos(self):
        """
        Retorna los nombres y apellidos completos
        :return:
        """
        return self.get_nombres() + ' ' + self.get_apellidos()

    def get_nombres_completos_inverso(self):
        """
        Retorna los nombres y apellidos completos de forma inversa
        :return:
        """
        return self.get_apellidos() + ' ' + self.get_nombres()


    def actualizar_datos_bsg(self, force=True, debug=True):
        """
        Actualiza los datos del registro civil, discapacidad y senescyt
        :param force:
        :param debug:
        :return:
        """
        self = Persona.crear_actualizar_persona_registro_civil(cedula=self.numero_documento,
                                                               actualizacion_forzada=force,
                                                               debug=debug)
        self.actualizar_discapacidad(debug=debug, force=force)
        self.actualizar_formacion_academica(debug=debug, force=force)
        return

    def actualizar_discapacidad(self, force=True, debug=True):
        """
        Actualizar discapacidad del Conadis
        :param force:
        :param debug:
        :return:
        """
        import unicodedata
        data = consultar_discapacidad_msp(self.numero_documento, force=force)
        if debug is True: print(data)
        if data:
            if 'FechaConadis' in data:
                self.discapacidad = True
                self.numero_carnet_conadis = data['CodigoConadis']
                self.fecha_registro_conadis = data['FechaConadis']
                self.porcentaje_discapacidad = data['PorcentajeDiscapacidad']

                # Grado de discapacidad
                grado_discapacidad = data['GradoDiscapacidad'].lower()
                catalogo_item_grado_discapacidad = CatalogoItem.objects.filter(catalogo__codigo='GRADO_DISCAPACIDAD',
                                                                               nombre__icontains=grado_discapacidad).first()
                if not catalogo_item_grado_discapacidad:
                    catalago_grado_discapacidad = Catalogo.objects.filter(codigo='GRADO_DISCAPACIDAD').first()
                    if not catalago_grado_discapacidad:
                        catalago_grado_discapacidad = Catalogo(codigo='GRADO_DISCAPACIDAD',
                                                               nombre='Grado de discapacidad',
                                                               descripcion='Grado de discapacida',
                                                               version=1)
                        catalago_grado_discapacidad.save()
                        if debug is True: print('catalogo', catalago_grado_discapacidad)
                    catalogo_item_grado_discapacidad = CatalogoItem(catalogo=catalago_grado_discapacidad,
                                                                    codigo_th=1,
                                                                    codigo_sg=1,
                                                                    nombre=grado_discapacidad)
                    catalogo_item_grado_discapacidad.save()
                    if debug is True: print('catalogo item', catalogo_item_grado_discapacidad)
                self.grado_discapacidad = catalogo_item_grado_discapacidad

                # Tipo de discapacidad, reemplazar tildes, a veces retorna con tilde o otras no
                tipo_discapacidad_NFKD = unicodedata.normalize('NFKD', data['DeficienciaPredomina'].lower())
                tipo_discapacidad = u"".join([c for c in tipo_discapacidad_NFKD if not unicodedata.combining(c)])
                catalogo_item_tipo_discapacidad = CatalogoItem.objects.filter(catalogo__codigo='TIPO_DISCAPACIDAD',
                                                                              nombre__icontains=tipo_discapacidad).first()
                if not catalogo_item_tipo_discapacidad:
                    catalago_tipo_discapacidad = Catalogo.objects.filter(codigo='TIPO_DISCAPACIDAD').first()
                    if not catalago_tipo_discapacidad:
                        catalago_tipo_discapacidad = Catalogo(codigo='TIPO_DISCAPACIDAD',
                                                              nombre='Tipo de discapacidad',
                                                              descripcion='Tipo de discapacidad',
                                                              version=1)
                        catalago_tipo_discapacidad.save()
                        if debug is True: print('catalogo', catalago_tipo_discapacidad)
                    catalogo_item_tipo_discapacidad = CatalogoItem(catalogo=catalago_tipo_discapacidad,
                                                                   codigo_th=1,
                                                                   codigo_sg=1,
                                                                   nombre=tipo_discapacidad)
                    catalogo_item_tipo_discapacidad.save()
                    if debug is True: print('catalogo item', catalogo_item_tipo_discapacidad)
                self.tipo_discapacidad = catalogo_item_tipo_discapacidad

                self.save()
                return

        self.discapacidad = False
        self.save()
        return

    def actualizar_formacion_academica(self, force=True, debug=True):
        """
        Actualiza información académica de la senescyt
        :param force:
        :param debug:
        :return:
        """
        from app.talento_humano.models import FormacionAcademica
        data = consultar_titulos_senescyt(self.numero_documento, force=force)
        if data is not None:
            if data != '' and data.niveltitulos:
                # Catalogos items
                ref_nivel = {'Nivel Técnico Superior': 'Nivel Técnico Superior',
                             'TECNICO': 'Nivel Técnico Superior',
                             'TERCER_NIVEL': 'Tercer Nivel o Pregrado',
                             'Tercer Nivel o Pregrado': 'Tercer Nivel o Pregrado',
                             'CUARTO_NIVEL': 'Cuarto Nivel o Posgrado',
                             'Cuarto Nivel o Posgrado': 'Cuarto Nivel o Posgrado',
                             'Educación Superior de Posgrado o Cuarto Nivel': 'Cuarto Nivel o Posgrado'}

                ref_nivel_instruccion = {'Nivel Técnico Superior': 'Técnico Superior',
                                         'TECNICO': 'Técnico Superior',
                                         'TERCER_NIVEL': 'Tercer Nivel',
                                         'Tercer Nivel o Pregrado': 'Tercer Nivel',
                                         'CUARTO_NIVEL': 'Cuarto Nivel - Maestria',
                                         'Cuarto Nivel o Posgrado': 'Cuarto Nivel - Maestria',
                                         'Educación Superior de Posgrado o Cuarto Nivel': 'Cuarto Nivel - Maestria'}
                nulos = ['null', 'None']

                # Expediente de la persona
                expediente = Expediente.objects.filter(persona=self).first()
                if expediente is None:
                    expediente = Expediente()
                    expediente.persona = self
                    expediente.save()

                for item in data.niveltitulos:
                    titulo = asdict(item.titulo[0])
                    numeroregistro = titulo.get('numeroRegistro')

                    # Obtiene le registro de formación academica o lo crea si no existe
                    formacion = FormacionAcademica.objects.filter(numero_registro=numeroregistro).first()
                    if formacion:
                        if formacion.validado_bsg:
                            continue
                        if formacion.expediente != expediente:
                            formacion = FormacionAcademica()
                            formacion.expediente = expediente
                            if debug is True: print("error: titulo con diferente usuario, título de %s-%s Nro:%s" % (
                                self.numero_documento, self.get_nombres_completos(), numeroregistro))
                    else:
                        formacion = FormacionAcademica()
                        formacion.expediente = expediente

                    # Fecha de registro
                    fecha_registro = None
                    if titulo.get('fechaRegistro'):
                        fecha_registro = datetime.datetime.strptime(titulo.get('fechaRegistro'), '%Y-%m-%d').date()
                    formacion.fecha_registro = fecha_registro

                    # Fecha de grado
                    fecha_grado = None
                    if titulo.get('fechaGrado'):
                        fecha_grado = datetime.datetime.strptime(titulo.get('fechaGrado'), '%Y-%m-%d').date()
                    formacion.fecha_grado = fecha_grado

                    # Nivel de instrucción
                    instruccion = None
                    if ref_nivel_instruccion.__contains__(titulo.get('nivel')):
                        instruccion = CatalogoItem.objects.filter(catalogo__codigo='NIVEL_INSTRUCCION',
                                                                  nombre__icontains=ref_nivel_instruccion.get(
                                                                      titulo.get('nivel'))).first()
                    else:
                        if debug is True: print('no existe el nivel de instrucción', titulo.get('nivel'))
                    formacion.nivel_instruccion = instruccion

                    # Tipo titulo
                    tipotitulo = CatalogoItem.objects.filter(catalogo__codigo='TIPO_TITULO',
                                                             nombre__icontains=titulo.get('tipoTitulo')).first()
                    if tipotitulo is None and titulo.get('tipoTitulo') not in nulos:
                        catalogo = Catalogo.objects.filter(codigo='TIPO_TITULO').first()
                        tipotitulo = CatalogoItem()
                        tipotitulo.codigo_th = 0
                        tipotitulo.nombre = titulo.get('tipoTitulo')
                        tipotitulo.catalogo = catalogo
                        tipotitulo.save()
                        if debug is True: print('agregado catalogoitem TIPO_TITULO: ', tipotitulo.nombre)
                    formacion.tipo_titulo = tipotitulo

                    # IES
                    if ref_nivel.__contains__(titulo.get('nivel')):
                        nivel_formacion = CatalogoItem.objects.filter(catalogo__codigo='NIVEL_FORMACION',
                                                                      nombre=ref_nivel.get(titulo.get('nivel'))).first()
                    else:
                        if debug is True: print('no tengo este nivel:', titulo.get('nivel'))
                        continue

                    ies = InsitucionEducativa.objects.filter(nombre=titulo.get('ies'),
                                                             nivel_formacion=nivel_formacion).first()
                    if ies:
                        formacion.institucion_educativa = ies
                        formacion.pais = ies.canton.provincia.pais if ies.canton else None
                    else:
                        formacion.institucion_educativo_otro = titulo.get('ies')

                    # Actualizo datos restantes
                    nombretitulo = titulo.get('nombreTitulo') if titulo.get('nombreTitulo') and titulo.get(
                        'nombreTitulo') != 'null' else None
                    area = titulo.get('area') if titulo.get('area') and titulo.get('area') not in nulos else None
                    subarea = titulo.get('subarea') if titulo.get('subarea') and titulo.get(
                        'subarea') not in nulos else None
                    clasificacion = titulo.get('nombreClasificacion') if titulo.get(
                        'nombreClasificacion') and titulo.get('nombreClasificacion') not in nulos else ''
                    observacion = titulo.get('observacion') if titulo.get('observacion') and titulo.get(
                        'observacion') not in nulos else ''

                    formacion.numero_registro = numeroregistro
                    formacion.titulo_obtenido = nombretitulo
                    formacion.area_conocimiento = '%s - %s' % (area, subarea) if area or subarea else ''
                    formacion.clasificacion = clasificacion
                    formacion.observacion = observacion
                    formacion.validado_bsg = True
                    formacion.save()
                    if debug is True: print('formacion', formacion.__dict__)
        return

    @staticmethod
    def crear_actualizar_persona_registro_civil(cedula=None, actualizacion_forzada=False, debug=True):
        """
        Metodo generico para actualizar o crear la persona con datos del registro Civil, se cambia el atributo
        persona.validado_bsg = True
        :param cedula: numero_documento
        :param actualizacion_forzada: vuelve a actualizar aún si está validada (persona.validado_bsg)
        :return: persona creada y validada, None si no existe en el Registro Civil
        """
        if debug is True: print('ingreso', cedula)
        if cedula:

            ref_estado_civ = {"VIUDO": 6, "SOLTERO": 4, "CASADO": 2, u"DIVORCIADO": 3, "EN UNION DE HECHO": 5}
            ref_genero = {'HOMBRE': 1, 'MUJER': 0}

            persona = Persona.objects.filter(numero_documento=cedula).first()
            if debug is True: print('consulta persona', persona)

            # Consulto del registro civil
            if persona is None or actualizacion_forzada:
                datos = consultar_por_cedula_regciv(cedula, force=actualizacion_forzada)
            else:
                if persona and persona.validado_bsg is False:
                    datos = consultar_por_cedula_regciv(cedula, force=actualizacion_forzada)
                else:
                    return persona
            if debug is True: print('datos', datos)

            #  Actualizo los datos o crea la persona siempre y cuando exista en el Registro civil
            if datos and datos.CodigoError == '000':
                try:
                    if persona is None:
                        persona = Persona()
                    primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = dividir_nombres_completos(
                        datos.Nombre)
                    persona.primer_nombre = primer_nombre
                    persona.segundo_nombre = segundo_nombre
                    persona.primer_apellido = primer_apellido
                    persona.segundo_apellido = segundo_apellido
                    persona.tipo_documento = CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO', 1)
                    persona.numero_documento = cedula
                    persona.fecha_nacimiento = datetime.datetime.strptime(datos.FechaNacimiento, '%d/%m/%Y')
                    persona.profesion = datos.Profesion

                    # Condición cedulado
                    condicion = CatalogoItem.objects.filter(catalogo__codigo='CONDICION_CEDULADO',
                                                            nombre__icontains=datos.CondicionCedulado).first()
                    if condicion is None:
                        catalogo = Catalogo.objects.filter(codigo='CONDICION_CEDULADO').first()
                        if debug is True: print('catalogo', catalogo)
                        condicion = CatalogoItem()
                        condicion.codigo_th = 0
                        condicion.nombre = datos.CondicionCedulado
                        condicion.catalogo = catalogo
                        condicion.save()
                        if debug is True: print('agregado catalogoitem CONDICION_CEDULADO: ', datos.CondicionCedulado)
                    persona.condicion_cedulado = condicion

                    # Estado civil
                    estado_civil = 4
                    if ref_estado_civ.__contains__(datos.EstadoCivil):
                        estado_civil = ref_estado_civ.get(datos.EstadoCivil)
                    else:
                        if debug is True: print('no hay este estado civil: ', datos.EstadoCivil)
                    persona.estado_civil = CatalogoItem.get_catalogo_item('ESTADO_CIVIL', estado_civil)

                    # Genero
                    sexo = 1
                    if ref_genero.__contains__(datos.Sexo):
                        sexo = ref_genero.get(datos.Sexo)
                    else:
                        if debug is True: print('no hay este genero: ', datos.Sexo)
                    persona.sexo = CatalogoItem.get_catalogo_item('TIPO_SEXO', sexo)

                    # Nacionalidad
                    nacionalidad = CatalogoItem.objects.filter(catalogo__codigo='NACIONALIDAD',
                                                               nombre__icontains=datos.Nacionalidad).first()
                    if nacionalidad:
                        persona.nacionalidad = nacionalidad
                    else:
                        if debug is True: print('nacionalidad no encontrada', datos.Nacionalidad)

                    persona.validado_bsg = True
                    persona.save()
                    if debug is True: print('sin error', persona)
                    return persona

                except Exception as e:
                    print(e)
                    return None
            return persona
        return None

    @staticmethod
    def buscar(criterio):
        """
        Buscar registros por criterios
        :param criterio:
        :return:
        """
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            for i in p_criterio:
                qset = qset & (
                        Q(primer_apellido__icontains=i) | Q(segundo_apellido__icontains=i) | Q(
                    primer_nombre__icontains=i) | Q(
                    segundo_nombre__icontains=i) | Q(numero_documento__icontains=i))
        return Persona.objects.filter(qset).distinct()

    @staticmethod
    def get_persona_numero_documento(numero_documento):
        """
        Busca la persona si existe por el numero de documento, caso contrario lo crea por el registro civil
        :param numero_documento:
        :return:
        """
        persona = Persona.objects.filter(numero_documento=numero_documento).first()
        if persona:
            return persona

        persona = Persona.crear_actualizar_persona_registro_civil(numero_documento)
        if persona:
            return persona

        return None


class Direccion(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tipo_direccion = models.ForeignKey(CatalogoItem,
                                       related_name='tipo_direccion',
                                       limit_choices_to={'catalogo__codigo': 'TIPO_DIRECCION'},
                                       on_delete=models.PROTECT)
    calle_principal = models.CharField(max_length=140)
    numero = models.CharField(max_length=140, null=True, blank=True)
    calle_secundaria = models.CharField(max_length=140, null=True, blank=True)
    referencia = models.CharField(max_length=140, null=True, blank=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    extension = models.CharField(max_length=30, null=True, blank=True)
    celular = models.CharField(max_length=30, null=True, blank=True)
    parroquia = models.ForeignKey(Parroquia, null=True, blank=True, on_delete=models.PROTECT)
    parroquia_otro = models.CharField(max_length=50, null=True, blank=True)

    def validar_celular(self):
        """
        Valida que exista el celular y tenga la longitud mínima
        :return:
        """
        if self.celular and len(self.celular) >= 10:
            return True
        return False

    def validar_telefono(self):
        """
        Valida que exista el número de telefono y tenga la longitud mínima
        :return:
        """
        if self.telefono and len(self.telefono) >= 9:
            return True
        return False

    def get_celular_o_telefono(self):
        """
        Retorna el celular o telefono
        :return:
        """
        if self.celular:
            return self.celular
        elif self.telefono:
            return (self.telefono + " " + self.extension).strip()
        return ''


class Expediente(models.Model):
    persona = models.OneToOneField(Persona, related_name='expediente', on_delete=models.CASCADE)


class Relacion(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE)
    contacto = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=20)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField(help_text='(AAAA-MM-DD)', null=True, blank=True)
    tipo_relacion = models.ForeignKey(CatalogoItem,
                                      related_name='tipo_relacion',
                                      limit_choices_to={'catalogo__codigo': 'TIPO_RELACION'},
                                      on_delete=models.PROTECT)
    tipo_documento = models.ForeignKey(CatalogoItem,
                                       related_name='relacion_tipo_documento',
                                       limit_choices_to={'catalogo__codigo': 'TIPO_DOCUMENTO'},
                                       on_delete=models.PROTECT)
    nivel_instruccion = models.ForeignKey(CatalogoItem,
                                          related_name='relacion_nivel_instruccion',
                                          limit_choices_to={'catalogo__codigo': 'NIVEL_INSTRUCCION'},
                                          null=True, blank=True, on_delete=models.SET_NULL)
    nepotismo = models.BooleanField(default=False, verbose_name=u"Trabaja en la misma institución")


class PeriodoFiscal(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField(blank=False, null=True,
                                    auto_now=False, auto_now_add=False)
    fecha_fin = models.DateField(blank=False, null=True,
                                 auto_now=False, auto_now_add=False)
    activo = models.NullBooleanField(default=False)

    def __str__(self):
        return self.nombre

    @staticmethod
    def get_periodo_fiscal_actual():
        today = datetime.date.today()
        return PeriodoFiscal.objects.filter(
            Q(fecha_inicio__lte=today) & Q(fecha_fin__gte=today) & Q(activo=True)).first()

    @staticmethod
    def get_periodo_fiscal(today=None):
        if today is None:
            today = datetime.date.today()

        return PeriodoFiscal.objects.filter(
            Q(fecha_inicio__lte=today) & Q(fecha_fin__gte=today)).first()


class PeriodoVacaciones(models.Model):
    """
    Se configura los periodos desde cuando a cuando se calculan representa el año de trabajo de acuerdo al calendario 
    dias_laborables = representa cuanto es el máximo de dias laborables que le corresponde
    dias_laborables_acumulados = cuantos dias de adelanto representa acumulacion de un fin de semana
    """
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField(blank=False, null=True,
                                    auto_now=False, auto_now_add=False)
    fecha_fin = models.DateField(blank=False, null=True,
                                 auto_now=False, auto_now_add=False)
    activo = models.NullBooleanField(default=False)
    dias_laborables = models.PositiveIntegerField(default=22)
    dias_laborables_acumulados = models.PositiveIntegerField(default=5)

    def __str__(self):
        return str(self.nombre) + ' Desde: ' + str(self.fecha_inicio) + ' Hasta: ' + str(self.fecha_fin)


class PeriodoVacionesRelacionLaboral(models.Model):
    """
    Agrupacion de los regimenes laborales y que periodo de vacación le corresponde para los diversos cálculos
    """
    periodo_vacaciones = models.ForeignKey('PeriodoVacaciones', on_delete=models.PROTECT)
    tipo_relacion_laboral = models.ForeignKey(CatalogoItem,
                                              null=True,
                                              limit_choices_to={'catalogo__codigo': 'TIPO_RELACION_LABORAL'},
                                              on_delete=models.PROTECT)
    activo = models.NullBooleanField(default=False)

    def __str__(self):
        return str(self.periodo_vacaciones) + ' - Para: ' + str(self.tipo_relacion_laboral) + ' - Activo: ' + (
            'Si' if self.activo else 'No')

    @staticmethod
    def get_periodos_vacaciones_activos(tipo_relacion_laboral, activo=None):
        if not activo is None:
            return PeriodoVacionesRelacionLaboral.objects.filter(tipo_relacion_laboral=tipo_relacion_laboral,
                                                                 activo=activo)
        return PeriodoVacionesRelacionLaboral.objects.filter(tipo_relacion_laboral=tipo_relacion_laboral)
