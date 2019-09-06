import os

import httplib2
import oauth2client
from apiclient import discovery
from django.conf import settings
from oauth2client import client
from oauth2client import tools
from unidecode import unidecode

# Scope de google
SCOPE_ADMIN = 'https://www.googleapis.com/auth/admin.directory.user'
SCOPE_GMAIL = 'https://apps-apis.google.com/a/feeds/emailsettings/2.0/'

# Credenciales
CREDENCIAL_ADMIN = 'admin-directory_v1.json'
CREDENCIAL_GMAIL = 'gmail-python-quickstart.json'


def get_credenciales(credencial, scope):
    """
    Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns: Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.siaaf')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, credencial)

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(settings.GOOGLE_CLIENT_SECRET_FILE, scope)
        flow.user_agent = settings.GOOGLE_APPLICATION_NAME
        credentials = tools.run(flow, store, None)
        print('Storing credentials to ' + credential_path)
    return credentials


def inicializar_consumir_api_google():
    """
    Metodo que debe ser ejecutado antes de consumir el api de Google. Autenticación
    con el API
    """
    credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)

    print('Getting the first 10 users in the domain')
    results = service.users().list(customer='my_customer', maxResults=10,
                                   orderBy='email').execute()
    users = results.get('users', [])

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print('{0} ({1})'.format(user['primaryEmail'],
                                     user['name']['fullName']))


def get_usuario(username):
    """
    Dado un nombre de usuario devuelve el usuario, caso contrario devuelve false
    """
    try:
        credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build("admin", "directory_v1", http=http)
        user_obj = service.users().get(userKey="{u}@{d}".format(u=username, d=settings.GOOGLE_DOMAIN)).execute()
        return user_obj
    except Exception as e:
        print(e)
        return False


def get_usuario_google(username):
    """
    Dado un nombre de usuario devuelve el usuario, si no existe devuelve false y si hay excepción devuelve None
    """
    try:
        credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build("admin", "directory_v1", http=http)
        user_obj = service.users().get(userKey="{u}@{d}".format(u=username, d=settings.GOOGLE_DOMAIN)).execute()
        return user_obj
    except Exception as e:
        if e.resp.status == 404:
            return False
        return None


def get_alias(username):
    """
    Dado un nombre de usuario devuelve el listado de alias que tiene dicha cuenta
    """
    try:
        credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build("admin", "directory_v1", http=http)
        user_obj = service.users().aliases().list(
            userKey="{u}@{d}".format(u=username, d=settings.GOOGLE_DOMAIN)).execute()
        return user_obj
    except:
        return False


def get_foto(username):
    """
    Dado un nombre de usuario devuelve datos de la fotografia
    """
    try:
        credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build("admin", "directory_v1", http=http)
        user_obj = service.users().photos().get(
            userKey="{u}@{d}".format(u=username, d=settings.GOOGLE_DOMAIN)).execute()
        return user_obj
    except:
        return False


def get_foto_base64(username):
    """
    Dado un nombre de usuario devuelve fotografia en base 64 y cambia los
    caracteres de acuerdo a documentación del API de google
    :param username:
    :return:
    """
    photo = get_foto(username)
    if photo:
        photo_data = str(photo.get('photoData'))
        s = photo_data.replace('_', '/')
        s = s.replace('-', '+')
        s = s.replace('*', '=')
        return s
    return None


def crear_usernames_str(primer_apellido, segundo_apellido, primer_nombre, segundo_nombre):
    """
    Forma el string del nombre de usuario de acuerdo a los nombres y apellidos
    :param primer_apellido:
    :param segundo_apellido:
    :param primer_nombre:
    :param segundo_nombre:
    :return:
    """
    return [unidecode('{0}.{1}'.format(primer_nombre, primer_apellido).lower()),
            unidecode('{0}.{1}.{2}'.format(primer_nombre, segundo_nombre[:1],
                                           primer_apellido).lower()),
            unidecode('{0}.{1}.{2}.{3}'.format(primer_nombre, segundo_nombre[:1],
                                               primer_apellido, segundo_apellido[:1]).lower())]


def nombre_usuario_disponible(primer_apellido, segundo_apellido, primer_nombre, segundo_nombre, cedula):
    """
    Crea el string username de acuerdo a los nombres y verifica si existe en google
    :param primer_apellido:
    :param segundo_apellido:
    :param primer_nombre:
    :param segundo_nombre:
    :param cedula:
    :return:
    """
    usernames = crear_usernames_str(primer_apellido, segundo_apellido, primer_nombre, segundo_nombre)
    nombre_usuario = None
    encontrado = False
    for nombre_usuario in usernames:
        usuario = get_usuario_google(nombre_usuario)
        if usuario:
            ext_ids = usuario.get('externalIds', [])
            for ext_id in ext_ids:
                if ext_id.get('value') == cedula:
                    return {'mensaje': 'Cedula ya existe en correos de google',
                            'nombre_usuario': nombre_usuario,
                            'estado': False}
        else:
            encontrado = True
            break
    return {'mensaje': 'Nombre encontrado',
            'nombre_usuario': nombre_usuario if encontrado else '',
            'estado': encontrado}


def crear_usuario_google(datos):
    """
    Crear un usuario en google
    :param datos:
           basicos:  {
               'name': {'familyName': 'Martinez',
                          'fullName': 'Jose Javier Martinez',
                          'givenName': 'Jose'},

                "password":"numero_cedula"
                "primaryEmail":""
                }

    :return:
    """
    if datos.get('name') and datos.get('password') and datos.get('primaryEmail'):
        try:
            credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
            http = credentials.authorize(httplib2.Http())
            service = discovery.build("admin", "directory_v1", http=http)
            datos.update({'changePasswordAtNextLogin': True})
            result = service.users().insert(body=datos).execute()
            return True
        except Exception as e:
            if e.resp and e.resp.status == 409:
                print("El nombre de usuario ya existe!! %s" % datos.get('primaryEmail'))

    return False


def actualizar_usuario_google(datos, userKey):
    """
    Actualiza un usuario en google
    :param datos:
           basicos:  {
               'name': {'familyName': 'Martinez',
                          'fullName': 'Jose Javier Martinez',
                          'givenName': 'Jose'},

                "password":"numero_cedula"
                "primaryEmail":""
                }

    :return:
    """
    if userKey:
        try:
            credentials = get_credenciales(CREDENCIAL_ADMIN, SCOPE_ADMIN)
            http = credentials.authorize(httplib2.Http())
            service = discovery.build("admin", "directory_v1", http=http)
            result = service.users().update(body=datos, userKey=userKey).execute()
            return True
        except Exception as e:
            print(e)

    return False
