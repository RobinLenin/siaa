from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE

try:
    from ldap3 import Server, Connection, SIMPLE, SYNC, ALL_ATTRIBUTES, SUBTREE
    from ldap3.core.exceptions import LDAPInvalidCredentialsResult
except ImportError:
    pass

from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def conectar():
    """
    Devuelve la conexión de ldad
    :return: conexion
    """
    try:
        server = Server(settings.LDAP_SERVER)
        conexion = Connection(server, settings.LDAP_AUTH, settings.LDAP_KEY, auto_bind=True)
        return conexion
    except Exception as e:
        print('error:ldap.conectar()', e)
        return None


def vincular_usuario_ldap(usuario):
    """
    Invoca a los metodos de modificar o crear el usuario en ldap
    :param usuario:
    :return:
    """
    if usuario.activo and usuario.google:
        if existe_usuario(usuario):
            return modificar_usuario_ldap(usuario)
        else:
            crear_usuario_ldap(usuario)
            # demf: Algunas veces no registra por algún dato faltante, por lo tanto verificar si se agregó correctamente
            return existe_usuario(usuario)
    return False


def obtener_tipo_de_clase(usuario):
    """
    Obtine la cadena de la organización para los usuarios
    :param usuario: El usuario para obtener tipo de clase a calcular
    :return: la cadena de la organización
    """
    tipo_de_clase = settings.LDAP_OU_DEFAULT
    # crea_sino_existe_unidad_organizacional('default', settings.LDAP_OU_BASE)
    if usuario.es_estudiante():
        tipo_de_clase = settings.LDAP_OU_ESTUDIANTE
    if usuario.es_funcionario():
        # crea_sino_existe_unidad_organizacional('funcionarios', settings.LDAP_OU_BASE)
        if usuario.funcionario.es_administrativo():
            tipo_de_clase = settings.LDAP_OU_ADMINISTRATIVO
            # crea_sino_existe_unidad_organizacional('administrativos', settings.LDAP_OU_FUNCIONARIO)
        if usuario.funcionario.es_docente():
            tipo_de_clase = settings.LDAP_OU_DOCENTE
            # crea_sino_existe_unidad_organizacional('docentes', settings.LDAP_OU_FUNCIONARIO)
        if usuario.funcionario.es_trabajador():
            tipo_de_clase = settings.LDAP_OU_TRABAJADOR
            # crea_sino_existe_unidad_organizacional('trabajadores', settings.LDAP_OU_FUNCIONARIO)
    return tipo_de_clase

def obtener_tipo_clase_cuenta(cuenta):
    """
    Obtine la cadena de la organización para los usuarios
    :param usuario: El usuario para obtener tipo de clase a calcular
    :return: la cadena de la organización
    """
    from app.seguridad.models import CuentaCorreo

    tipo_de_clase = settings.LDAP_OU_DEFAULT

    if cuenta.tipo == CuentaCorreo.TIPO_ESTUDIANTES:
        tipo_de_clase = settings.LDAP_OU_ESTUDIANTE

    if cuenta.tipo == CuentaCorreo.TIPO_DOCENTES:
        tipo_de_clase = settings.LDAP_OU_DOCENTE

    if cuenta.tipo == CuentaCorreo.TIPO_TRABAJADORES:
        tipo_de_clase = settings.LDAP_OU_TRABAJADOR

    if cuenta.tipo == CuentaCorreo.TIPO_SERVIDORES:
        tipo_de_clase = settings.LDAP_OU_ADMINISTRATIVO

    print('tipo_de_clase:', tipo_de_clase)

    return  tipo_de_clase



def crear_usuario_ldap(usuario):
    """
    Crea el usuario en Ldap
    :param usuario:
    :return:
    """
    try:
        conexion = conectar()
        tipo_clase = obtener_tipo_de_clase(usuario)
        persona = usuario.persona
        direccion = persona.get_direccion_domicilio()
        dn = 'uid=' + usuario.correo_electronico_institucional + ',' + tipo_clase
        conexion.add(dn, ['inetOrgPerson', 'organizationalPerson', 'eduPerson', 'top', 'person'], {
            'cn': persona.get_nombres().upper(),
            'sn': persona.get_apellidos().upper(),
            'givenName': persona.get_nombres().upper(),
            'userPassword': persona.numero_documento,
            'eduPersonTargetedID': persona.numero_documento,
            'eduPersonPrincipalName': usuario.correo_electronico_institucional,
            'uid': usuario.correo_electronico_institucional,
            'mail': usuario.correo_electronico_institucional,
            'ou': tipo_clase.split(',')[0].replace("ou=", ""),
            'telephoneNumber': direccion.get_celular_o_telefono() if direccion else 'S/N'
        })
        print('CREADO: ' + dn)
        return True
    except:
        return False


def crear_usuario_ldap_of_cuenta_correo(cuenta):
    try:
        conexion = conectar()
        tipo_clase = obtener_tipo_clase_cuenta(cuenta)
        dn = 'uid=' + cuenta.email_institucional + ',' + tipo_clase
        conexion.add(dn, ['inetOrgPerson', 'organizationalPerson', 'eduPerson', 'top', 'person'], {
            'cn': cuenta.nombres.upper(),
            'sn': cuenta.apellidos.upper(),
            'givenName': cuenta.nombres.upper(),
            'userPassword': cuenta.numero_documento,
            'eduPersonTargetedID': cuenta.numero_documento,
            'eduPersonPrincipalName': cuenta.email_institucional,
            'uid': cuenta.email_institucional,
            'mail': cuenta.email_institucional,
            'ou': tipo_clase.split(',')[0].replace("ou=", ""),
            'telephoneNumber': cuenta.celular if cuenta.celular else (cuenta.telefono if cuenta.telefono else 'S/N'),
        })
        print('CREADO: ' + dn)
        return True
    except Exception as e:
        print(e)
        return False


def modificar_usuario_ldap(usuario):
    """
    Modifica el usuario en Ldap
    :param usuario:
    :return:
    """
    try:
        conexion = conectar()
        entradas = existe_usuario(usuario)
        if len(entradas) < 1:
            return None
        persona = usuario.persona
        direccion = persona.get_direccion_domicilio()
        dn = entradas[0].entry_dn
        conexion.modify(dn, {
            'cn': [(MODIFY_REPLACE, [persona.get_nombres().upper()])],
            'sn': [(MODIFY_REPLACE, [persona.get_apellidos().upper()])],
            'givenName': [(MODIFY_REPLACE, [persona.get_nombres().upper()])],
            'eduPersonTargetedID': [(MODIFY_REPLACE, [persona.numero_documento])],
            'eduPersonPrincipalName': [(MODIFY_REPLACE, [usuario.correo_electronico_institucional])],
            'mail': [(MODIFY_REPLACE, [usuario.correo_electronico_institucional])],
            'telephoneNumber': [(MODIFY_REPLACE, [direccion.get_celular_o_telefono() if direccion else 'S/N'])],
        })
        print('ACTUALIZADO: ', dn)
        mover_usuario_ldap(usuario, dn)
        return True
    except:
        return False


def modificar_password_by_uid_ldap(uid, password):
    """
    Modifica la contraseña del usuario por el uuid
    :param usuario: El usuario a quien se va a modificar el usuario
    :return: Si pudo cambiarse la contraseña
    """
    try:
        conexion = conectar()
        entradas = existe_usuario_by_uid(uid)
        if len(entradas) < 1:
            return None
        dn = entradas[0].entry_dn
        print(dn)
        conexion.modify(dn, {
            'userPassword': [(MODIFY_REPLACE, [password])],
        })
        return True
    except:
        return False


def modificar_password_by_usuario_ldap(usuario, password):
    """
    Modifica la contraseña del usuario por username
    :param usuario: El usuario a quien se va a modificar el usuario
    :return: Si pudo cambiarse la contraseña
    """
    try:
        conexion = conectar()
        entradas = existe_usuario(usuario)
        if len(entradas) < 1:
            return None
        dn = entradas[0].entry_dn
        print(dn)
        conexion.modify(dn, {
            'userPassword': [(MODIFY_REPLACE, [password])],
        })
        mover_usuario_ldap(usuario, dn)
        return True
    except:
        return False


def mover_usuario_ldap(usuario, dn):
    """
    Cambia al usuario de directorio en Ldap
    :param usuario:
    :param dn:
    :return:
    """
    try:
        conexion = conectar()
        dn_nuevo = 'cn=' + usuario.correo_electronico_institucional
        nuevo_superior = obtener_tipo_de_clase(usuario)
        print(dn)
        print(dn_nuevo)
        print(nuevo_superior)
        conexion.modify_dn(dn, dn_nuevo, new_superior=obtener_tipo_de_clase(usuario))
        print('MOVIDO: ' + dn_nuevo)
        return True
    except:
        print(conexion.result)
        return False


def existe_usuario_by_uid(uid):
    try:
        conexion = conectar()
        conexion.search('dc=unl,dc=edu,dc=ec',
                        '(&(objectclass=person)(uid=' + uid + '))')
        return conexion.entries
    except  Exception as e:
        print('error:ldap.existe_usuario()', e)
        return None


def existe_usuario(usuario):
    return existe_usuario_by_uid(usuario.correo_electronico_institucional)


def existe_unidad_organizacional(ou, base=None, ):
    try:
        if base == None:
            base = settings.LDAP_OU_BASE
        conexion = conectar()
        conexion.search(base, '(&(objectclass=organizationalUnit)(ou=' + ou + '))')
        return conexion.entries
    except:
        return None


def crear_unidad_organizacional(ou, base):
    try:
        conexion = conectar()
        dn = 'ou=' + ou + ',' + base
        conexion.add(dn, 'organizationalUnit')
    except:
        return None


def crea_sino_existe_unidad_organizacional(ou, base=None):
    if base == None:
        base = settings.LDAP_OU_BASE
    if not existe_unidad_organizacional(ou, base):
        crear_unidad_organizacional(ou, base)


def existe_grupo_ldap(grupo_numero, base=None, ):
    try:
        if base == None:
            base = settings.LDAP_OU_GRUPO
        conexion = conectar()
        conexion.search(base, '(&(objectclass=posixGroup)(gidNumber=' + grupo_numero + '))')
        return conexion.entries
    except:
        return None


def crear_grupo_ldap(grupo):
    try:
        conexion = conectar()
        dn = 'cn=' + grupo.nombre + ',' + settings.LDAP_OU_GRUPO
        crea_sino_existe_unidad_organizacional('grupos', settings.LDAP_OU_BASE)
        return conexion.add(dn, ['posixGroup', 'top'], {'description': grupo.descripcion, 'gidNumber': grupo.id})
    except:
        return None


def modificar_grupo_ldap(grupo):
    try:
        conexion = conectar()
        entradas = existe_grupo_ldap(str(grupo.id))
        if len(entradas) < 1:
            return None
        dn = entradas[0].entry_dn
        conexion.modify(dn, {'description': [(MODIFY_REPLACE, [grupo.descripcion])]})
        conexion.modify_dn(dn, 'cn=' + grupo.nombre)
        return conexion.result
    except:
        return False


def vincular_grupo_ldap(grupo):
    if existe_grupo_ldap(str(grupo.id)):
        return modificar_grupo_ldap(grupo)
    else:
        return crear_grupo_ldap(grupo)


def agregar_usuario_a_grupo_ldap(grupo, usuario):
    try:
        conexion = conectar()
        entradas = existe_grupo_ldap(str(grupo.id))
        if len(entradas) > 0:
            dn = entradas[0].entry_dn
            if not existe_usuario(usuario):
                vincular_usuario_ldap(usuario)
            if not existe_usuario_en_grupo_ldap(grupo, usuario):
                conexion.modify(dn, {'memberUid': [(MODIFY_ADD, [usuario.correo_electronico_institucional])]})
                return conexion.result
        return None
    except:
        return None


def eliminar_usuario_a_grupo_ldap(grupo, usuario):
    try:
        if existe_usuario_en_grupo_ldap(grupo, usuario):
            conexion = conectar()
            entradas = existe_grupo_ldap(str(grupo.id))
            if len(entradas) > 0:
                dn = entradas[0].entry_dn
                conexion.modify(dn, {'memberUid': [(MODIFY_DELETE, [usuario.correo_electronico_institucional])]})
                return conexion.result
        return None
    except:
        return None


def existe_usuario_en_grupo_ldap(grupo, usuario):
    try:
        conexion = conectar()
        entradas = existe_grupo_ldap(str(grupo.id))
        if len(entradas) > 0:
            dn = entradas[0].entry_dn
            return conexion.compare(dn, 'memberUid', usuario.correo_electronico_institucional)
        return None
    except:
        return None


def _autenticar(username=None, password=None, search_filter='(uid={})', search_base=settings.LDAP_OU_BASE):
    """
    Autentica y retorna el dn
    :param username:
    :param password:
    :param search_filter:
    :param search_base:
    :return:
    """
    valid_info = None
    server = Server(settings.LDAP_SERVER)
    c = Connection(server, authentication=SIMPLE, client_strategy=SYNC, raise_exceptions=True)
    c.open()

    current_search_filter = search_filter.format(username)  # Example: '(uid={})'

    if c.search(search_base=search_base, search_filter=current_search_filter, search_scope=SUBTREE,
                attributes=ALL_ATTRIBUTES):
        user_information = c.response[0]
        user_dn = user_information["dn"]
        attrs = user_information['attributes']
        print('attrs -> ', attrs)

        user_data = {'identificacion': attrs['eduPersonTargetedID'][0], 'mail': attrs['mail'][0],
                     'apellidos': attrs['sn'][0], 'nombres': attrs['cn'][0], 'telefono': attrs['telephoneNumber'][0],
                     'password': attrs['userPassword'][0]}

        c = Connection(server, authentication=SIMPLE, user=user_dn, password=password, client_strategy=SYNC,
                       raise_exceptions=True)
        c.open()
        try:
            c.bind()
            valid_info = user_data
        except LDAPInvalidCredentialsResult as e:
            # check response
            # --> ldap3.__version__ == '0.9.7.4' seems to throw and exception even when the bind is successful...
            #     check the response's 'description'
            if hasattr(e, "description"):
                if e.description == "success":
                    valid_info = user_data
                else:
                    logger.warning(
                        "LDAPInvalidCredentialsResult raised {} ({}) login attempt".format(e.description, username))
            else:
                logger.warning(
                    "LDAPInvalidCredentialsResult raised on ({}) login attempt, no 'response' attached to exception.".format(
                        username))
    else:
        # search failed!
        logger.error('LDAP Connection.search() failed for: {}'.format(current_search_filter))

    return valid_info

def consultar_informacion_ldap(username=None, search_filter='(uid={})', search_base=settings.LDAP_OU_BASE):
    """
    Autentica y retorna el dn
    :param username:
    :param search_filter:
    :param search_base:
    :return:
    """
    valid_info = None
    server = Server(settings.LDAP_SERVER)
    c = Connection(server, authentication=SIMPLE, client_strategy=SYNC, raise_exceptions=True)
    c.open()

    current_search_filter = search_filter.format(username)  # Example: '(uid={})'

    if c.search(search_base=search_base, search_filter=current_search_filter, search_scope=SUBTREE,
                attributes=ALL_ATTRIBUTES):
        user_information = c.response[0]
        user_dn = user_information["dn"]
        attrs = user_information['attributes']
        print('attrs -> ', attrs)

        user_data = {'identificacion': attrs['eduPersonTargetedID'][0], 'mail': attrs['mail'][0],
                     'apellidos': attrs['sn'][0], 'nombres': attrs['cn'][0], 'telefono': attrs['telephoneNumber'][0],
                     'password': attrs['userPassword'][0]}

        return user_data

    return None


def autenticar_siaaf(username=None, password=None):
    """
    Authenticar using LDAP PARA iniciar sesión en el SIAAF
    :param username:
    :param password:
    :return:
    """
    valid_info = _autenticar(username, password)
    if valid_info:
        # now = timezone.now()
        # exact_username = user_information['attributes']["uid"][0]
        # first_name = " ".join(user_information['attributes']["givenName"])
        # last_name = " ".join(user_information["attributes"]["sn"])
        # email = user_information['attributes']['mail'][0]
        try:
            from app.seguridad.models import Usuario
            user = Usuario.objects.get(correo_electronico_institucional__exact=username)
            # always update proteus user profile to synchronize ldap server
            if password == user.persona.numero_documento:
                user.force_password = True
            user.set_password(password)
            user.save()
        #         user.first_name = first_name
        #         user.last_name = last_name
        #         user.email = email
        #         user.last_login = now
        #         user.save()
        #         logger.info("({}) logged in.".format(username))
        except Usuario.DoesNotExist:
            logger.info("({}) logged in - initial".format(username))
            return False
    #         # crear nuevo usuario
    #         user = Usuario()
    #         user.username = exact_username
    #         user.set_password(password)
    #         user.first_name = first_name
    #         user.last_name = last_name
    #         user.email = email
    #         user.is_staff = True
    #         user.is_superuser = True
    #         user.is_active = True
    #         user.last_login = now
    #         user.save()
    return valid_info


def autenticar_by_uid_or_targetedID(username=None, password=None):
    """
    Authenticate using LDAP, solo en grupo docentes. Se invoca desde sga-docentes
    :param username:
    :param password:
    :return:
    """
    username_search_filter = '(uid={})'.format(username)
    identifi_search_filter = '(eduPersonTargetedID={})'.format(username)
    search_filter = username_search_filter if '@' in username else identifi_search_filter

    valid_info = _autenticar(username, password, search_filter=search_filter, search_base=settings.LDAP_OU_BASE)

    return valid_info
