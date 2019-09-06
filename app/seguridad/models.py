# -*- coding: utf-8 -*-
import unidecode
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from app.core.models import Persona
from app.core.utils import google
from app.core.utils.google import get_usuario
from app.core.utils.ldap import modificar_password_by_usuario_ldap, vincular_usuario_ldap, vincular_grupo_ldap, \
    agregar_usuario_a_grupo_ldap, eliminar_usuario_a_grupo_ldap
from app.seguridad.utils.username import get_username


class FuncionalidadManager(models.Manager):
    """
    Modelo para poder referenciar a una funcionalidad por su código
    """

    def get_by_natural_key(self, codigo):
        return self.get(codigo=codigo)


class Funcionalidad(models.Model):
    MODULO_SIAAF = 'S'
    MODULO_ANGULAR = 'A'
    TIPO_MODULO = (
        (MODULO_ANGULAR, 'Angular'),
        (MODULO_SIAAF, 'Siaaf'),
    )
    nombre = models.CharField(max_length=250)
    formulario = models.CharField(max_length=250)
    orden = models.IntegerField()
    padre = models.ForeignKey('self', blank=True,
                              related_name='funcionalidades', null=True, on_delete=models.SET_NULL)
    activo = models.NullBooleanField(default=False)
    mostrar = models.NullBooleanField(default=False)
    codigo = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=1,
                              choices=TIPO_MODULO,
                              default=MODULO_ANGULAR, )

    objects = FuncionalidadManager()

    class Meta:
        ordering = ('nombre',)
        unique_together = ('codigo',)

    def __str__(self):
        return self.nombre

    objects = FuncionalidadManager()


class FuncionalidadGroup(models.Model):
    group = models.ForeignKey('auth.Group', verbose_name=u'Group',
                              related_name='funcionalidadesGroups', on_delete=models.CASCADE)
    funcionalidad = models.ForeignKey('Funcionalidad',
                                      verbose_name=u'Funcionalidad',
                                      related_name='funcionalidadesGroups', on_delete=models.CASCADE)

    class Meta:
        ordering = ('group',)

    def __str__(self):
        return self.funcionalidad.nombre + " " + self.group.name


class ManejadorUsuarios(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Usuario debe tener un correo valido.')

        if not kwargs.get('username'):
            raise ValueError('El usuario debe tener un nombre valido.')

        account = self.model(
            email=self.normalize_email(email), username=kwargs.get('username')
        )

        account.set_password(password)
        account.save()

        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)
        account.is_admin = True
        account.save()

        return account


class Usuario(AbstractBaseUser, PermissionsMixin):
    activo = models.BooleanField(default=False)
    correo_electronico_institucional = models.EmailField(unique=True, blank=True)
    foto_url = models.TextField(blank=True, max_length=7000, null=True)
    google = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    ldap = models.BooleanField(default=False)
    force_password = models.BooleanField(default=True)  # Forzar cambio de contraseña

    nombre_de_usuario = models.CharField(max_length=50, unique=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'correo_electronico_institucional'
    REQUIRED_FIELDS = [correo_electronico_institucional]

    objects = ManejadorUsuarios()

    class Meta:
        ordering = ['persona', 'nombre_de_usuario']

    def __str__(self):
        return self.nombre_de_usuario

    def cargar_funcionalidades(self, modulo):
        """
        Retorna la funcionalidades del usuario ya sea django o angular
        :param modulo:
        :return:
        """
        qset = Q(funcionalidadesGroups__group__user=self, activo=True, modulo=modulo)
        respuesta = []
        funcionalidades_padre = Funcionalidad.objects.filter(qset, padre_id__isnull=True).distinct().order_by('orden').all()
        for funcionalidad in funcionalidades_padre:
            respuesta.append({'nombre': funcionalidad.nombre,
                              'icon': funcionalidad.icon,
                              'formulario': funcionalidad.formulario,
                              'hijas': self.cargar_funcionalidad_hijas(funcionalidad, qset)})

        return respuesta

    def cargar_funcionalidad_hijas(self, funcionalidad, qset):
        """
        Devuelve una lista de funcionalidades hijas
        :param funcionalidad:
        :param qset: Para filtrar segun el modulo al que pertenece
        :return:
        """
        hijas = []
        for fun in funcionalidad.funcionalidades.filter(qset).distinct().order_by('orden').all():
            hijas.append({'nombre': fun.nombre,
                          'icon': fun.icon,
                          'formulario': fun.formulario,
                          'hijas': self.cargar_funcionalidad_hijas(fun, qset)})
        return hijas

    def es_estudiante(self):
        """
        Decuelve True si el usuario es estudiante y estado activo
        :return:
        """
        if hasattr(self, 'estudiante'):
            return self.estudiante.activo
        return False

    def es_funcionario(self):
        """
        Decuelve True si el usuario es funcionario y estado activo
        :return:
        """
        if hasattr(self, 'funcionario'):
            return self.funcionario.activo
        return False

    def funcionalidades_angular(self):
        """
        Obtien las funcionalidades del usuario de angular
        :return:
        """
        return self.cargar_funcionalidades(Funcionalidad.MODULO_ANGULAR)

    def funcionalidades_siaaf(self):
        """
        Obtiene la funcionalidades del usuario de django
        :return:
        """
        return self.cargar_funcionalidades(Funcionalidad.MODULO_SIAAF)

    def get_short_name(self):
        """
        Requerido pora ingresar al admin de django, retorna el nombre de usuario
        :return:
        """
        return self.nombre_de_usuario

    def is_member(self, nombre_grupo):
        """
        Valida si el usuario es admin o pertenece a un grupo específico
        :param nombre_de_grupo:
        :return:
        """
        if self.is_admin:
            return True
        else:
            return self.groups.filter(name=nombre_grupo).exists()

    def is_staff(self):
        """
        Requerido pora ingresar al admin de django, valida si es admin
        :return:
        """
        return self.is_admin

    def get_nombre_usuario_temporal(self):
        """
        Retorna un nombre de usuario generado que no exista en el API del gmail y que no este utilizado
        en la tabla Usuario como credenciales de acceso ya que el nombre de usuario debe ser único
        :return:
        """
        if not self.persona:
            return None

        # Combinación 1: Si existe el usuario en gmail (TRUE) o si esta creado el usuario con estas credenciales
        nombre_usuario = '{0}.{1}'.format(self.persona.primer_nombre,
                                          self.persona.primer_apellido).lower()
        nombre_usuario = nombre_usuario.replace("ñ", "n")
        usuario = Usuario.objects.filter(nombre_de_usuario=nombre_usuario).first()
        if google.get_usuario(nombre_usuario) or usuario:
            # Combinación 2: Si existe el usuario en gmail o si esta creado el usuario con estas credenciales
            nombre_usuario = '{0}.{1}.{2}'.format(self.persona.primer_nombre,
                                                  self.persona.segundo_nombre[:1],
                                                  self.persona.primer_apellido).lower()
            nombre_usuario = nombre_usuario.replace("ñ", "n")
            usuario = Usuario.objects.filter(nombre_de_usuario=nombre_usuario).first()
            if google.get_usuario(nombre_usuario) or usuario:
                # Combinación 3: Si existe el usuario en gmail o si esta creado el usuario con estas credenciales
                nombre_usuario = '{0}.{1}.{2}.{3}'.format(self.persona.primer_nombre,
                                                          self.persona.segundo_nombre[:1],
                                                          self.persona.primer_apellido,
                                                          self.persona.segundo_apellido[:1]).lower()
                nombre_usuario = nombre_usuario.replace("ñ", "n")
                usuario = Usuario.objects.filter(nombre_de_usuario=nombre_usuario).first()
                if google.get_usuario(nombre_usuario) or usuario:
                    # Combinación 4: Usuario con el número de cédula
                    nombre_usuario = '{0}.{1}'.format(nombre_usuario, self.persona.numero_documento)

        return nombre_usuario

    def get_nombre_de_usuario(self):
        """
        Retorna el nombre de usuario sin @
        :return:
        """
        if self.validar_correo_institucional():
            self.nombre_de_usuario = self.correo_electronico_institucional.strip().split('@unl.edu.ec')[0]
            return self.nombre_de_usuario
        else:
            return None

    def resetear_contrasena(self):
        """
        Resetea la contraseña al número de identificacion en:
        * Usuario  SIAAF
        * Usuario LDAP
        :return:
        """
        self.set_password(self.persona.numero_documento)
        self.force_password = True
        if settings.LDAP_ACTIVE and self.ldap:
            modificar_password_by_usuario_ldap(self, self.persona.numero_documento)
        self.save()
        return

    def valida_capacitacion(self):
        """
        Valida la capacitacion del usuario, ya sea funcionario, estudiante, alumni
        :return:
        """
        if self.es_funcionario():
            return self.funcionario.valida_capacitacion()

        return False

    def validar_correo_institucional(self, correo=None):
        """
        Valida el correo electronico
        :param correo:
        :return:
        """
        if not correo:
            correo = self.correo_electronico_institucional

        if correo.find('@unl.edu.ec') < 0:
            return False
        else:
            self.correo_electronico_institucional = correo
            return True

    def valida_datos_personales(self):
        """
        Valida datos personales del usuario ya sea funcionario, estudiante, alumni
        :return:
        """
        if self.es_funcionario():
            return self.funcionario.valida_datos_personales()

        return False

    def valida_direccion(self):
        """
        Valida direción del usuario ya sea funcionario, estudiante, alumni
        :return:
        """
        if self.es_funcionario():
            return self.funcionario.valida_direccion()

        return False

    def valida_formacion(self):
        """
        Valida formación académica del usuario ya sea funcionario, estudiante, alumni
        :return:
        """
        if self.es_funcionario():
            return self.funcionario.valida_formacion()

        return False

    def valida_relacion(self):
        """
        Valida relacion familiar del usuario ya sea funcionario, estudiante, alumni
        :return:
        """
        if self.es_funcionario():
            return self.funcionario.valida_relacion()

        return False

    def valida_produccion_cientifica(self):
        """
        Valida producción científica del usuario ya sea funcionario, estudiante, alumni
        :return:
        """
        if self.es_funcionario():
            return self.funcionario.valida_produccion_cientifica()

        return False

    def valida_trayectoria_laboral(self):
        """
        Valida trayectoria laboral del usuario ya sea funcionario, estudiante, alumni
        :return:view_usuario
        """
        if self.es_funcionario():
            return self.funcionario.valida_trayectoria_laboral()

        return False

    def vincular_ldap(self):
        """
        Agrega un usuario al servidor ldap
        :return:
        """
        self.ldap = False
        if vincular_usuario_ldap(self):
            self.ldap = True
        self.save()
        return self.ldap

    def vincular_google(self):
        """
        Vincula la cuenta con google. La variable google significa que
        se ha vinculado la fotografía de la cuenta google
        :return:
        """
        self.google = False
        self.foto_url = None

        user_google = get_usuario(self.nombre_de_usuario)
        if user_google:
            self.google = True
            url = user_google.get('thumbnailPhotoUrl')
            if url:
                self.foto_url = url
        self.save()
        return self.google


    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        """
        Crea el token al crear un usuario
        :param instance:
        :param created:
        :param kwargs:
        :return:
        """
        if created:
            Token.objects.create(user=instance)

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
                qset = qset & (Q(persona__primer_apellido__icontains=i) | Q(
                    correo_electronico_institucional__icontains=i) | Q(
                    persona__segundo_apellido__icontains=i) | Q(
                    persona__primer_nombre__icontains=i) | Q(
                    persona__segundo_nombre__icontains=i) | Q(
                    persona__numero_documento__icontains=i))
        return Usuario.objects.filter(qset).distinct()

    @staticmethod
    def get_usuario_numero_documento(numero_documento):
        """
        Busca el usuario si existe por el numero de documento, caso contrario crea el usuario
        :param numero_documento:
        :return:
        """
        usuario = Usuario.objects.filter(persona__numero_documento=numero_documento).first()
        if usuario:
            return usuario

        persona = Persona.get_persona_numero_documento(numero_documento)
        if persona:
            usuario = Usuario(persona=persona)
            usuario.nombre_de_usuario = usuario.get_nombre_usuario_temporal()
            usuario.correo_electronico_institucional = usuario.nombre_de_usuario + '@unl.edu.ec'
            usuario.set_password(numero_documento)
            try:
                usuario.save()
            except:
                # Por lo general cuando ya esta registrado el correo y nombre de usuario salta el error y hay que cambiar
                usuario.nombre_de_usuario = usuario.nombre_de_usuario + usuario.persona.numero_documento
                usuario.correo_electronico_institucional = usuario.nombre_de_usuario + usuario.persona.numero_documento + '@unl.edu.ec'
                usuario.save()
            usuario.persona.actualizar_formacion_academica()
            return usuario

        return None


class GrupoLDAP(models.Model):
    """
    Representación de un grupo de Ldap
    """
    nombre = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=400)
    ldap = models.BooleanField(default=False)
    usuarios = models.ManyToManyField(Usuario)
    eliminado = models.BooleanField(default=False)


    def __str__(self):
        return str(self.nombre)

    def agregar_usuario_grupo_ldap(self, usuario):
        """
        Agrega un @Usuario al grupo LDAP, siempre y cuando el grupo yá este creado y agurdado en la BD
        :param usuario:
        :return:Verdadero o Falso de acuerdo al resultado de la transacción
        """
        if not self.id:
            return False
        return agregar_usuario_a_grupo_ldap(self, usuario)

    def eliminar_usuario_grupo_ldap(self, usuario):
        """
        Remueve un usuario de un determinado grupo de ldap
        :param usuario: el Usuario a remover
        :return: el resultado
        """
        if not self.id:
            return False
        return eliminar_usuario_a_grupo_ldap(self, usuario)

    def vincular_ldap(self):
        """
        Permite vincular un grupo a LDAP: Si el grupo no existe en LDAP lo crea
        :return: Verdadero o Falso de acuerdo al resultado de la actualización
        """
        if not self.id:
            return False
        if vincular_grupo_ldap(self):
            self.ldap = True
            self.save()
            return True
        return False


class CuentaCorreo(models.Model):
    """
    Representación una cuenta de correo google
    """
    TIPO_DOCENTES = 'docentes'
    TIPO_ESTUDIANTES = 'estudiantes'
    TIPO_SERVIDORES = 'servidores'
    TIPO_TRABAJADORES = 'trabajadores'
    TIPO_OTROS = 'otros'
    TIPO_CHOICES = (
        (TIPO_DOCENTES, u'Docentes'),
        (TIPO_ESTUDIANTES, u'Estudiantes'),
        (TIPO_SERVIDORES, u'Servidores'),
        (TIPO_TRABAJADORES, u'Trabajadores'),
        (TIPO_OTROS, u'Otros')
    )
    numero_documento = models.CharField(max_length=20, unique=True, blank=False, null=False)
    email_institucional = models.EmailField(unique=True, blank=False, null=False)
    email_alternativo = models.EmailField(blank=True, null=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default=TIPO_OTROS)
    nombres = models.CharField(max_length=250)
    apellidos = models.CharField(max_length=250)
    email_name = models.CharField(max_length=500, null=True)
    telefono = models.CharField(max_length=250, blank=True, null=True)
    celular = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return str(self.email_institucional)

    def asociar_cuenta_google(self):
        """
        Actualiza la cuenta de correo en google
        :return:
        """
        data = {
            'organizations': [{'description': self.tipo, 'primary': True}],
            'externalIds': [{'type': 'organization', 'value': self.numero_documento}]
        }
        return google.actualizar_usuario_google(data, userKey=self.email_institucional)

    def crear_cuenta_google(self):
        """
        Crea la cuenta de correo en google
        :return:
        """
        data = {
            'name': {'familyName': self.apellidos.title(),
                     'fullName': ('%s %s' % (self.apellidos, self.nombres)).title(),
                     'givenName': self.nombres.title()},
            "password": self.numero_documento,
            "primaryEmail": self.email_institucional,
            'phones': [],
            'emails': [],
            'organizations': [{'description': self.tipo, 'primary': True}],
            'externalIds': [{'type': 'organization', 'value': self.numero_documento}]
        }
        if self.telefono:
            data.get('phones').append({'type': 'home', 'value': self.telefono})
        if self.celular:
            data.get('phones').append({'type': 'mobile', 'value': self.celular})
        if self.email_alternativo:
            data.get('emails').append({'type': 'home', 'address': self.email_alternativo})
        return google.crear_usuario_google(data)

    def is_email_name_valid(self):
        """
        Valida los nombre y apellidos de la cuenta de google de la bd con el email_name
        :return:
        """
        local_names = [(self.nombres + ' ' + self.apellidos), (self.apellidos + ' ' + self.nombres)]
        u_local_name = unidecode.unidecode(self.email_name.strip().lower())
        for name in local_names:
            u_name = unidecode.unidecode(name.strip().lower())
            if u_local_name == u_name:
                return True
        return False

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
                        Q(apellidos__icontains=i) |
                        Q(nombres__icontains=i) |
                        Q(email_institucional__icontains=i) |
                        Q(numero_documento__icontains=i))
        return CuentaCorreo.objects.filter(qset).distinct()

    @staticmethod
    def query_cuenta_correo_by_datatable_params(params):
        """
        Busca por los parámetros indicados del datatable
        :param params:
        :return:
        """
        #Contar total de registros
        queryset = CuentaCorreo.objects.all()
        params.total = queryset.count()

        #Aplica filtros
        if params.search_value:
            qset = Q()
            for sValue in params.get_search_values():
                qset = qset & (
                        Q(apellidos__icontains=sValue) |
                        Q(nombres__icontains=sValue) |
                        Q(email_institucional__icontains=sValue) |
                        Q(numero_documento__icontains=sValue))
            queryset = CuentaCorreo.objects.filter(qset)

        #Contar total de registros aplicando el filtro
        params.count = queryset.count()

        #Extraer los resultados aplicando filtros y paginación y longitud de la página
        params.items = params.init_items(queryset)
        return params

class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50, verbose_name='Creado por')
    updated_by = models.CharField(max_length=50, verbose_name='Actualizado por')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        req = get_username()
        if not self.pk:
            self.created_by = str(req.user)
        self.updated_by = str(req.user)
        super(AuditModel, self).save(*args, **kwargs)
