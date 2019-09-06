from uuid import uuid1

import pytz
from suds.client import Client
from suds.sax.element import Element
from suds.sudsobject import Object as SudsObject
from suds.sudsobject import asdict

from app.bsg.models import PersonaBsg, DiscapacidadBsg, TituloBsg
from app.configuracion.utils.enums import EnumDetalleParametrizacion
from app.bsg.utils.enums import ServiciosBSG, SecurityHeader

utc = pytz.UTC

# TIEMPO EN DÍAS
TIEMPO_CONSULTA_BSG_REGISTRI_CIVIL = 180
TIEMPO_CONSULTA_BSG_CONADIS = 180
TIEMPO_CONSULTA_BSG_SENESCYT = 30


def consultar_por_cedula_regciv(cedula, force=True):
    """
    Método que permite retornar  los datos de una persona del registro civil y los guarda en la tabla del esquema de bsg
    :param cedula: Persona a buscar
    :param force: Si es True consulta del registro civil y actualiza los datos en BD y si el False consulta de BD
    :return: Devuelve un dict con los datos personales del propietario de la cedula ingresada como parámetro
    {'codigoError': '000', 'error': 'CONSULTA REALIZADA.', 'Calle': '', 'CondicionCedulado'......]}
    """
    from datetime import datetime, timedelta

    if force is True:
        response = consultar_por_cedula_regciv_bsg(cedula)
        if response and response.CodigoError == '000':
            defaults = PersonaBsg.get_defaults(Client.dict(response))
            person, created = PersonaBsg.objects.update_or_create(NUI=cedula, defaults=defaults)
    else:
        person = PersonaBsg.objects.filter(NUI=cedula).first()
        fechaConsultar = person.FechaConsulta + timedelta(days=TIEMPO_CONSULTA_BSG_REGISTRI_CIVIL) if person else None

        if person is None or (person and fechaConsultar < datetime.now()):
            response = consultar_por_cedula_regciv_bsg(cedula)
            if response and response.CodigoError == '000':
                defaults = PersonaBsg.get_defaults(Client.dict(response))
                person, created = PersonaBsg.objects.update_or_create(NUI=cedula, defaults=defaults)
        else:
            response = person.get_object_suds()
            response.CodigoError = '000'

    return response


def consultar_por_nombre_regciv(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, force=True):
    """
    Método que permite retornar  los datos de una persona del registro civil y los guarda en la tabla del esquema de bsg
    :param nombres: Persona a buscar
    :param force: Si es True consulta del registro civil y actualiza los datos en BD y si el False consulta de BD
    :return: Devuelve un dict con los datos personales del propietario
    {'codigoError': '000', 'error': 'CONSULTA REALIZADA.', 'persona': [<suds.sudsobject.ciudadano at 0x7fe60ad92160>]}
    """
    from datetime import datetime, timedelta

    if force is True:
        response = consultar_por_nombre_regciv_bsg(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido)
        if response and response.codigoError == '000':
            # Retorna una lista de personas
            defaults = asdict(response.persona[0])
            person, created = PersonaBsg.objects.update_or_create(NUI=defaults['NUI'], defaults=defaults)
    else:
        nombre = '%s %s %s %s' % (primer_apellido, segundo_apellido, primer_nombre, segundo_nombre)
        person = PersonaBsg.objects.filter(Nombre__iexact=nombre.upper()).first()
        fechaConsultar = person.FechaConsulta + timedelta(days=TIEMPO_CONSULTA_BSG_REGISTRI_CIVIL) if person else None

        if person is None or (person and fechaConsultar < datetime.now()):
            response = consultar_por_nombre_regciv_bsg(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido)
            if response and response.codigoError == '000':
                # Retorna una lista de personas
                defaults = asdict(response.persona[0])
                person, created = PersonaBsg.objects.update_or_create(NUI=defaults['NUI'], defaults=defaults)
        else:
            response = SudsObject()
            response.codigoError = '000'
            response.persona = [person.get_object_suds()]

    return response


def consultar_discapacidad_msp(cedula, force=True):
    """
    Método que permite retornar los datos de una persona con discapacidad del Ministerio de Salud Pública y los guarda en la tabla del esquema de bsg
    :param cedula: Persona a buscar
    :param force: Si es True consulta del Conadis y actualiza los datos en BD y si el False consulta de BD
    :return: Devuelve un dict con los datos personales e informacion de discapacidad del propietario de la cédula
    que se ingresa como parámetro.
    {'CodigoConadis': '11.7088', 'DeficienciaPredomina': 'PSICOLOGICO', 'GradoDiscapacidad': 'Moderado'......}
    """
    from datetime import datetime, timedelta

    if force is True:
        response = consultar_discapacidad_msp_bsg(cedula)
        if response:
            #FechaConadis en algunos casos no está fijado
            defaults = asdict(response) if ('FechaConadis' in response or 'CodigoConadis' in response) else {'NumeroIdentificacion': cedula}
            discapacidadObj, created = DiscapacidadBsg.objects.update_or_create(NumeroIdentificacion=cedula,
                                                                                defaults=defaults)
    else:
        discapacidad = DiscapacidadBsg.objects.filter(NumeroIdentificacion=cedula).first()
        fechaConsultar = discapacidad.FechaConsulta + timedelta(
            days=TIEMPO_CONSULTA_BSG_CONADIS) if discapacidad else None
        if discapacidad is None or (discapacidad and fechaConsultar < datetime.now()):
            response = consultar_discapacidad_msp_bsg(cedula)
            if response:
                defaults = asdict(response) if ('FechaConadis' in response or 'CodigoConadis' in response) else {'NumeroIdentificacion': cedula}
                discapacidadObj, created = DiscapacidadBsg.objects.update_or_create(NumeroIdentificacion=cedula,
                                                                                    defaults=defaults)
        else:
            response = discapacidad.get_object_suds()
            if 'CodigoConadis' not in response:
                response.Mensaje = "No se encontro discapacitado"

    return response


def consultar_titulos_senescyt(cedula, force=True):
    """
    Método que permite retornar los datos de titulos registrados en el SENESCYT de un Titulado y los guarda en la tabla del esquema de bsg
    :param cedula: Persona a buscar
    :param force: Si es True consulta del Registro Civil y actualiza los datos en BD y si el False consulta de BD
    :return: Devuelve un dict con la información de los titulos registrados en el SENESCYT del propietario de la cedula.
    {'niveltitulos': [{titulo: [{'fechaGrado': '2005-08-24',...}]},{titulo},{titulo},...]}
    """
    from datetime import datetime, timedelta
    import pytz
    utc = pytz.UTC
    if force is True:
        response = consultar_titulos_senescyt_bsg(cedula)
        if response and 'niveltitulos' in response:
            for niveltitulo in response.niveltitulos:
                titulo = asdict(niveltitulo.titulo[0])
                tituloObj, created = TituloBsg.objects.update_or_create(numeroIdentificacion=cedula,
                                                                        numeroRegistro=titulo['numeroRegistro'],
                                                                        defaults=titulo)
    else:
        titulosSenecyt = TituloBsg.objects.filter(numeroIdentificacion=cedula).order_by('FechaConsulta').all()
        fechaConsultar = titulosSenecyt.first().FechaConsulta + timedelta(days=TIEMPO_CONSULTA_BSG_SENESCYT) if len(
            titulosSenecyt) > 0 else None

        if len(titulosSenecyt) == 0 or (len(titulosSenecyt) > 0 and fechaConsultar < datetime.now()):
            response = consultar_titulos_senescyt_bsg(cedula)
            if response and 'niveltitulos' in response:
                for niveltitulo in response.niveltitulos:
                    titulo = asdict(niveltitulo.titulo[0])
                    tituloObj, created = TituloBsg.objects.update_or_create(numeroIdentificacion=cedula,
                                                                            numeroRegistro=titulo['numeroRegistro'],
                                                                            defaults=titulo)
        else:
            response = SudsObject()
            response.niveltitulos = []

            for titulo in titulosSenecyt:
                tituloObjectSuds = SudsObject()
                tituloObjectSuds.titulo = []
                tituloObjectSuds.titulo.append(titulo.get_object_suds())

                response.niveltitulos.append(tituloObjectSuds)

    return response


def consultar_por_cedula_regciv_bsg(cedula):
    """
    Método que permite retornar en los datos una persona en el registro civil
    :param cedula:
    :return: Devuelve un dict con los datos personales del propietario de la cedula ingresada como parámetro
    """
    from app.configuracion.models import DetalleParametrizacion
    # noinspection PyBroadException
    try:
        url = ServiciosBSG.buscarPorCedulaRegCiv.value
        usuariobsg = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSG.value).first()
        validador = validador_bsg(usuariobsg.valor, url)
        client = Client(url)
        headers = create_security_header(usuariobsg.valor, validador.Digest, validador.Nonce, validador.Fecha,
                                         validador.FechaF)
        client.set_options(soapheaders=headers)
        client.set_options(port='ConsultaCiudadanoPort')
        username = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSGRC.value).first()
        password = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.CLAVE_BSGRC.value).first()
        institucion = DetalleParametrizacion.objects.filter(
            codigo=EnumDetalleParametrizacion.INSTITUCION_BSGRC.value).first()
        agencia = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.AGENCIA_BSGRC.value).first()
        response = client.service.BusquedaPorNui(NUI=cedula, CodigoInstitucion=institucion.valor,
                                                 CodigoAgencia=agencia.valor, Usuario=username.valor,
                                                 Contrasenia=password.valor)
        return response
    except Exception as e:
        print(e)
        return None


def consultar_por_nombre_regciv_bsg(primer_nombre, segundo_nombre, primer_apellido, segundo_apellido):
    """
     Método que permite retornar en los datos una persona en el registro civil
    :param primer_nombre:
    :param segundo_nombre:
    :param primer_apellido:
    :param segundo_apellido:
    :return:
    """
    from app.configuracion.models import DetalleParametrizacion
    # noinspection PyBroadException
    try:
        url = ServiciosBSG.buscarPorCedulaRegCiv.value
        usuariobsg = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSG.value).first()
        validador = validador_bsg(usuariobsg.valor, url)
        client = Client(url)
        headers = create_security_header(usuariobsg.valor, validador.Digest, validador.Nonce, validador.Fecha,
                                         validador.FechaF)
        client.set_options(soapheaders=headers)
        client.set_options(port='ConsultaCiudadanoPort')
        username = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSGRC.value).first()
        password = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.CLAVE_BSGRC.value).first()
        institucion = DetalleParametrizacion.objects.filter(
            codigo=EnumDetalleParametrizacion.INSTITUCION_BSGRC.value).first()
        agencia = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.AGENCIA_BSGRC.value).first()

        if primer_nombre is None:
            primer_nombre = ""
        if segundo_nombre is None:
            segundo_nombre = ""
        if primer_apellido is None:
            primer_apellido = ""
        if segundo_apellido is None:
            segundo_apellido = ""
        response = client.service.BusquedaPorNombre(CodigoInstitucion=institucion.valor,
                                                    CodigoAgencia=agencia.valor, Apellido1=primer_apellido,
                                                    Apellido2=segundo_apellido,
                                                    Nombre1=primer_nombre, Nombre2=segundo_nombre, EdadInicio='',
                                                    EdadFinal='', Sexo='',
                                                    Usuario=username.valor,
                                                    Contrasenia=password.valor)
        return response
    except Exception as e:
        print(e)
        return None


def consultar_discapacidad_msp_bsg(cedula):
    """
    Método que permite retornar los datos de una persona con discapacidad del Ministerio de Salud Pública
    :param cedula:
    :return: Devuelve un dict con los datos personales e informacion de discapacidad del propietario de la cédula
    que se ingresa como parámetro.
    """
    from app.configuracion.models import DetalleParametrizacion
    # noinspection PyBroadException
    try:
        url = ServiciosBSG.consultarDiscapacidadBSGMSP.value
        usuariobsg = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSG.value).first()
        validador = validador_bsg(usuariobsg.valor, url)
        client = Client(url)
        headers = create_security_header(usuariobsg.valor, validador.Digest, validador.Nonce, validador.Fecha,
                                         validador.FechaF)
        client.set_options(soapheaders=headers)
        client.set_options(port='WebServiceSnapDiscapacidadesPort')
        username = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSGMSP.value).first()
        password = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.CLAVE_BSGMSP.value).first()
        response = client.service.BuscarPersonaConDiscapacidad(Identificacion=cedula, Usuario=username.valor,
                                                               Clave=password.valor)
        return response
    except Exception as e:
        print(e)
        return None


def consultar_titulos_senescyt_bsg(cedula):
    """
    Método que permite retornar los datos de titulos registrados en el SENESCYT de un Titulado.
    :param cedula:
    :return: Devuelve un dict con la información de los titulos registrados en el SENESCYT del propietario de la cedula.
    """
    from app.configuracion.models import DetalleParametrizacion
    # noinspection PyBroadException
    try:
        url = ServiciosBSG.consultarTitulosBSGSENESCYT.value
        usuariobsg = DetalleParametrizacion.objects.filter(codigo=EnumDetalleParametrizacion.USUARIO_BSG.value).first()
        validador = validador_bsg(usuariobsg.valor, url)
        client = Client(url)
        headers = create_security_header(usuariobsg.valor, validador.Digest, validador.Nonce, validador.Fecha,
                                         validador.FechaF)
        client.set_options(soapheaders=headers)
        client.set_options(port='WSConsultaTitulosServicePort')
        response = client.service.ConsultadeTitulosRequest(CedulaTitulado=cedula)
        return response
    except Exception as e:
        print(e)
        return None


def validador_bsg(usuario, url_ws):
    """
    Método que permite validar un servicio del Bus de Datos Gubernamental (BSG).
    :param usuario:
    :param url_ws:
    :return: Devuelve datos de validacion como Digest, Nonce, Fecha de Inicio, Fecha de Fin
    """
    # noinspection PyBroadException
    try:
        url = ServiciosBSG.bsgValidador.value
        client = Client(url)
        r = client.factory.create('validarPermisoPeticion')
        r.Cedula = usuario
        r.Urlsw = url_ws
        response = client.service.ValidarPermiso(r)
        return response
    except Exception as e:
        print(e)
        return None


def create_security_header(username, password, nonce, fecha, fecha_fin):
    """
    Permite generar un tabla-header de seguridad en xml para posteriormente en la peticion a cualquier servicio del
    Bus de Datos Gubernamental (BSG) agregarlo en la cabecera
    :param username:
    :param password:
    :param nonce:
    :param fecha:
    :param fecha_fin:
    :return: tabla-header de seguridad en xml
    """

    # Namespaces
    wsse = (SecurityHeader.wsseElement.value, SecurityHeader.wsse.value)
    wsu = (SecurityHeader.wsuElement.value, SecurityHeader.wsu.value)

    # Create Security Element
    security = Element(SecurityHeader.securityElement.value, ns=wsse)
    # security.set('SOAP-ENV:mustUnderstand', '1')

    # Create UsernameToken, Username/Pass Element
    usernametoken = Element(SecurityHeader.usernameToken.value, ns=wsse)

    # Add the wsu namespace to the Username Token. This is necessary for the created date to be included.
    usernametoken.set('xmlns:wsu', SecurityHeader.xmlnsWsu.value)
    usernametoken.set('wsu:Id', 'SecurityToken-' + str(uuid1()))

    # Add the username token to the security header. This will always be 'session'
    uname = Element(SecurityHeader.username.value, ns=wsse).setText(username)
    # Add the password element and set the type to 'PasswordText'.
    # This will be nosession on the initialize() call, and the returned sessionID on subsequent calls.
    passwd = Element(SecurityHeader.passwordElement.value, ns=wsse).setText(password)
    passwd.set(SecurityHeader.typeElement.value, SecurityHeader.passwordType.value)
    # Add a nonce element to further uniquely identify this message.
    nonce = Element(SecurityHeader.nonceElement.value, ns=wsse).setText(nonce)
    nonce.set(SecurityHeader.encodingTypeElement.value, SecurityHeader.encodingTypeNonce.value)
    # Add the current time in UTC format.
    created = Element(SecurityHeader.createdElement.value, ns=wsu).setText(str(fecha))

    # Add Username, Password, Nonce, and Created elements to UsernameToken element.
    # Python inserts tags at the top, and Learn needs these in a specific order, so they are added in reverse order
    usernametoken.insert(created)
    usernametoken.insert(nonce)
    usernametoken.insert(passwd)
    usernametoken.insert(uname)

    # Insert the usernametoken into the wsse:security tag
    security.insert(usernametoken)

    timestamp = Element(SecurityHeader.timestampElement.value, ns=wsu)
    timestamp.set('wsu:Id', 'Timestamp-' + str(uuid1()))
    createdt = Element(SecurityHeader.createdElement.value, ns=wsu).setText(fecha)
    expires = Element(SecurityHeader.expiresTimestampElement.value, ns=wsu).setText(fecha_fin)
    timestamp.insert(expires)
    timestamp.insert(createdt)
    security.insert(timestamp)
    # Return the security XML
    return security
