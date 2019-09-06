import csv
import logging as log
from datetime import datetime

from app.bienes.models import *
from app.configuracion.models import *
from app.core.models import Catalogo
from app.core.utils import general
from app.core.utils.general import dividir_nombres_completos, dividir_nombres_o_apellidos
from app.seguridad.models import CuentaCorreo
from app.bsg.views import *
from app.talento_humano.models import Funcionario

def crear_correos_institucionales(archivo=None):
    """
    Crea direcciones de correo institucional en Google a partir de un .csv. Se crea los correos institucionales utilizando
    archivo google_utils, formatos de correos: jose.martinez, jose.j.martinez, jose.j.martinez.o
    :param Archivo csv a ser procesado columnas necesarias: CEDULA, NOMBRES, APELLIDOS, CORREO, TELEFONO, CELULAR , ORGANIZACION
    :return error_correos_no_existe {.csv}: Números de cédulas que no se encuentran registradas o ya tiene relación con usuario.
    :return logs {dic}: Visualiza el log resultante del proceso
    """
    from django.conf import settings
    from app.core.utils.google import nombre_usuario_disponible

    csvsalida = open(archivo.replace('.csv', '_result.csv'), 'w', )
    salida = csv.writer(csvsalida, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    salida.writerow(['CEDULA', 'CORREO CREADO', 'NOMBRE USUARIO', 'NOMBRES', 'APELLIDOS', 'MENSAJE'])

    with open(archivo, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            correo = row.get('CORREO')
            telefono = row.get('TELEFONO')
            celular = row.get('CELULAR')
            tipo = row.get('ORGANIZACION')
            cedula = row.get('CEDULA')
            datos = None
            mensaje = [cedula, '-', '', row.get('NOMBRES'), row.get('APELLIDOS'), '']
            try:
                if len(cedula) == 10 and cedula.isdigit():
                    datos = consultar_por_cedula_regciv(cedula, force=False)
            except Exception as e:
                mensaje[5] = 'no es cedula, se crea con datos de csv'
            if datos and datos.CodigoError == '000':
                primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = dividir_nombres_completos(
                    datos.Nombre)
            else:
                primer_apellido, segundo_apellido = dividir_nombres_o_apellidos(row.get('APELLIDOS'))
                primer_nombre, segundo_nombre = dividir_nombres_o_apellidos(row.get('NOMBRES'))
            username_temp = nombre_usuario_disponible(primer_apellido, segundo_apellido, primer_nombre, segundo_nombre,
                                                      cedula)

            nombre_usuario = username_temp.get('nombre_usuario')
            email_institucional = "{u}@{d}".format(u=nombre_usuario, d=settings.GOOGLE_DOMAIN)

            if username_temp.get('estado'):
                cuenta_correo = CuentaCorreo.objects.filter(
                    Q(numero_documento=cedula) | Q(email_institucional=email_institucional)).first()
                if cuenta_correo:
                    mensaje[2] = cuenta_correo.email_institucional
                    mensaje[5] = 'Ya existe esta CuentaCorreo'
                else:
                    cuenta_correo = CuentaCorreo(numero_documento=cedula,
                                                 email_institucional=email_institucional,
                                                 email_alternativo=correo,
                                                 tipo=tipo,
                                                 nombres=('%s %s' % (primer_nombre, segundo_nombre)).lower(),
                                                 apellidos=('%s %s' % (primer_apellido, segundo_apellido)).lower(),
                                                 telefono=telefono,
                                                 celular=celular)
                if cuenta_correo.crear_cuenta_google():
                    mensaje[2] = cuenta_correo.email_institucional
                    mensaje[1] = 'SI'
                    cuenta_correo.save()
                else:
                    mensaje[1] = 'NO'
                    mensaje[5] = 'Error al crear el usuario en metodo crear_usuario_google'
            else:

                mensaje[1] = 'NO'
                mensaje[2] = email_institucional
                mensaje[5] = username_temp.get('mensaje')
            salida.writerow(mensaje)
    csvsalida.close()


def generar_reporte_emails_existentes(archivo, archivo_destino):
    """
    Verifica si los emails del archivo tiene asociado un funcionario activo del SIAAF
    :param archivo:
    :param archivo_destino:
    :return:
    """
    documento = open(archivo, 'r')
    documento_destino = open(archivo_destino, 'w')
    lineas = documento.readlines()
    for l in lineas:
        email = l.replace('\n', '')
        print(email)
        d = Persona.objects.filter(usuario__correo_electronico_institucional=email, usuario__isnull=False).first()

        if d is not None and d.usuario.es_funcionario() is True:
            texto = '%s|%s|%s|%s%s' % (
                d.primer_nombre + " " + d.segundo_nombre, d.primer_apellido + " " + d.segundo_apellido,
                email, d.numero_documento, '\n')
            documento_destino.write(texto)
    documento_destino.close()


def validar_email_gsuite_all(archivo=None, destino=None):
    """
    Valida si el listado de correos es válido, es decir si existe en gsuite
    :param archivo:
    :param destino:
    :return:
    """
    from app.core.utils.google import get_usuario_google
    try:
        with open(archivo, 'r') as csvfile:
            documento = open(destino, 'w')
            texto = u'Email|Existe|\n'
            documento.write(texto)
            reader = csv.DictReader(csvfile)
            index = 1
            for row in reader:
                user_name = row['email'].split('@')[0]
                result = get_usuario_google(user_name) if user_name else None
                documento.write(row['email'])
                if result:
                    texto = u'|%s|' % ('SI',)
                    documento.write(texto)
                else:
                    documento.write('|NO|')
                index = index + 1
                documento.write('\n');
            documento.close()
    except Exception as e:
        log.error('Error al validar emails %s', e)
    return None


def crear_personas_por_registro_civil(archivo=None):
    """
    Crea Personas de acuerdo al archivo, si hay error con el servicios_web la creo a la persona sin validar la info.
    :param archivo: Lista de personas, 2 campos requeridos con encabezados: 'cedula','nombres'
    :return: array de creados y errores: [creados,ya_validados,creado_manualmente,error_nombres, error_datos, error_cedulas]
    """
    print('Inicio cargando estudiantes')
    if archivo:
        with open(archivo, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            error_datos = []
            error_cedulas = []
            error_nombres = []
            creados = []
            ya_validados = []
            creado_manualmente = []
            for row in reader:
                numero_documento = row['cedula']
                persona = Persona.objects.filter(numero_documento=numero_documento).first()
                if persona is None:
                    persona = crear_actualizar_persona_registro_civil(cedula=numero_documento)
                    if persona is None:
                        validado = True
                        if persona is None:
                            persona = Persona()
                            if len(row['cedula']) == 10 or len(row['cedula']) == 13:
                                validado = general.verificar_ci(numero_documento)
                        if validado:
                            nombres = row['nombres']
                            primer_apellido, segundo_apellido, primer_nombre, segundo_nombre = dividir_nombres_completos(
                                nombres)
                            persona.primer_nombre = primer_nombre
                            persona.segundo_nombre = segundo_nombre
                            persona.primer_apellido = primer_apellido
                            persona.segundo_apellido = segundo_apellido
                            persona.tipo_documento = CatalogoItem.get_catalogo_item('TIPO_DOCUMENTO', 1)
                            persona.numero_documento = numero_documento
                            persona.sexo = CatalogoItem.get_catalogo_item('TIPO_SEXO', 1)
                            persona.validado_bsg = False
                            persona.save()
                            creado_manualmente.append(persona)
                        else:
                            error_cedulas.append(row)
                    else:
                        creados.append(persona)
                else:
                    if persona.validado_bsg:
                        ya_validados.append(persona)
                    else:
                        persona = crear_actualizar_persona_registro_civil(cedula=numero_documento)
                        creados.append(persona)

            print('terminado...')
            print(
                'creados(%s), ya validados-no modificados(%s), creados_manualmente(%s), revisar nombres(%s), error al guardar datos(%s), error_cedula(%s)' % (
                    len(creados), len(ya_validados), len(creado_manualmente), len(error_nombres), len(error_datos),
                    len(error_cedulas)))
            return [creados, ya_validados, creado_manualmente, error_nombres, error_datos, error_cedulas]


def crear_actualizar_persona_registro_civil(cedula=None, actualizacion_forzada=False):
    """
    Actualiza un objeto persona con datos del registro Civil, se cambia el atributo persona.validado_bsg = True
    :param cedula: numero_documento
    :param actualizacion_forzada: vuelve a actualizar aún si está validada (persona.validado_bsg)
    :return: persona creada y validada, None si no existe en el Registro Civil
    """
    if cedula:
        ref_estado_civ = {"VIUDO": 6, "SOLTERO": 4, "CASADO": 2, u"DIVORCIADO": 3, "EN UNION DE HECHO": 5}
        ref_genero = {'HOMBRE': 1, 'MUJER': 0}
        persona = Persona.objects.filter(numero_documento=cedula).first()
        datos = None
        if persona is None or actualizacion_forzada or (persona and persona.validado_bsg is False):
            datos = consultar_por_cedula_regciv(cedula, force=False)
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
                persona.fecha_nacimiento = datetime.strptime(datos.FechaNacimiento, '%d/%m/%Y')

                condicion = CatalogoItem.objects.filter(catalogo__codigo='CONDICION_CEDULADO',
                                                        nombre__icontains=datos.CondicionCedulado).first()
                if condicion is None:
                    catalogo = Catalogo.objects.filter(codigo='CONDICION_CEDULADO').first()
                    condicion = CatalogoItem()
                    condicion.codigo_th = 0
                    condicion.nombre = datos.CondicionCedulado
                    condicion.catalogo = catalogo
                    condicion.save()
                    print('agregado catalogoitem CONDICION_CEDULADO: ', datos.CondicionCedulado)
                persona.condicion_cedulado = condicion
                persona.profesion = datos.Profesion
                estado_civil = 4
                if ref_estado_civ.__contains__(datos.EstadoCivil):
                    estado_civil = ref_estado_civ.get(datos.EstadoCivil)
                else:
                    print('no hay este estado civil: ', datos.EstadoCivil)
                persona.estado_civil = CatalogoItem.get_catalogo_item('ESTADO_CIVIL', estado_civil)
                sexo = 1
                if ref_genero.__contains__(datos.Sexo):
                    sexo = ref_genero.get(datos.Sexo)
                else:
                    print('no tengo este genero: ', datos.Sexo)
                persona.sexo = CatalogoItem.get_catalogo_item('TIPO_SEXO', sexo)
                nacionalidad = CatalogoItem.objects.filter(catalogo__codigo='NACIONALIDAD',
                                                           nombre__icontains=datos.Nacionalidad).first()
                if nacionalidad:
                    persona.nacionalidad = nacionalidad
                else:
                    print('nacionalidad no encontrada', datos.Nacionalidad)
                persona.validado_bsg = True
                persona.save()
                return persona
            except Exception as e:
                return None
    return None


def getVal(obj: None, attr: None):
    """
    Retorna el valor de un atributo
    :param obj:
    :param attr:
    :return:
    """
    if hasattr(obj, attr):
        return obj[attr]
    else:
        return ''


def consultar_datos_rg_all(archivo=None, destino=None):
    """
    Consulta los datos en el registro civil
    Si no encuentra nada escribe una línea solo con la cédula para mantener la misma districuón del archivo original
    :param archivo:
    :param destino:
    :return:
    """
    try:
        with open(archivo, 'r') as csvfile:
            documento = open(destino, 'w')
            texto = u'Cedula|Nombre|FechaNacimiento|LugarNacimiento|Nacionalidad|Sexo|Genero|EstadoCivil|Domicilio|Calle|NumeroCasa|Instrucción|Profesión|Conyuge|NombreMadre|NombrePadre|\n'
            documento.write(texto)
            reader = csv.DictReader(csvfile)
            index = 1
            for row in reader:
                result = consultar_por_cedula_regciv(row['cedula'], force=False)
                documento.write(row['cedula'])

                print('consultando', index, row['cedula'], result)
                if result is not None and 'Mensaje' not in result:
                    if 'Nombre' in result:
                        print(index, 'Cedula', row['cedula'])
                        texto = u'|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % (
                            result['Nombre'],
                            result['FechaNacimiento'],
                            result['LugarNacimiento'],
                            result['Nacionalidad'],
                            result['Sexo'],
                            result['Genero'],
                            result['EstadoCivil'],

                            result['Domicilio'],
                            result['Calle'],
                            result['NumeroCasa'],

                            result['Instruccion'],
                            result['Profesion'],

                            result['Conyuge'],
                            result['NombreMadre'],
                            result['NombrePadre']
                        )
                        documento.write(texto)

                index = index + 1
                documento.write('\n');
            documento.close()
    except Exception as e:
        log.error('Error al exportar estudiantes %s', e)
    return None


def consultar_datos_senescyt_all_single_line(archivo=None, destino=None):
    """
    @autor: Danny Muñoz
    @fecha: 2018-06-08
    Consulta datos del senescyt y muestra todos los titulos de cada cédula en una misma línea.
    :param archivo:
    :param destino:
    :return:
    """
    try:
        errores_rc = []
        with open(archivo, 'r') as csvfile:
            documento = open(destino, 'w')
            thead = u'|area%s|areaCodigo|fechaGrado|fechaRegistro|ies|nivel|nombreClasificacion|nombreTitulo|numeroRegistro|observacion|subarea|subareaCodigo|tipoExtranjeroColegio|tipoNivel|tipoTitulo'
            texto = u'identificacion'
            for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                texto = texto + (thead % n)
            documento.write(texto + '\n')
            reader = csv.DictReader(csvfile)
            index = 1
            for row in reader:
                titulos = consultar_titulos_senescyt(row['cedula'], force=False)

                print('consultando senescyt', index, row['cedula'], titulos)
                documento.write(row['cedula'])

                if titulos is not None and 'niveltitulos' in titulos:
                    for item in titulos['niveltitulos']:
                        for subitem in item['titulo']:
                            texto = u'|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % (
                                getVal(subitem, 'area'),
                                getVal(subitem, 'areaCodigo'),
                                getVal(subitem, 'fechaGrado'),
                                getVal(subitem, 'fechaRegistro'),
                                getVal(subitem, 'ies'),
                                getVal(subitem, 'nivel'),
                                getVal(subitem, 'nombreClasificacion'),
                                getVal(subitem, 'nombreTitulo'),
                                getVal(subitem, 'numeroRegistro'),
                                getVal(subitem, 'observacion'),
                                getVal(subitem, 'subarea'),
                                getVal(subitem, 'subareaCodigo'),
                                getVal(subitem, 'tipoExtranjeroColegio'),
                                getVal(subitem, 'tipoNivel'),
                                getVal(subitem, 'tipoTitulo'),
                            )
                            documento.write(texto)

                documento.write('\n')
                index = index + 1

            documento.close()

            return errores_rc
    except Exception as e:
        log.error('Error al exportar titulos %s', e)
    return None


def consultar_datos_senescyt_all(archivo=None, destino=None):
    """
    @autor: Danny Muñoz
    @fecha: 2018-07-23
    Consulta los titulos en el senescy, por cada titulo retorna en una línea
    :param archivo:
    :param destino:
    :return:
    """
    try:
        errores_rc = []
        with open(archivo, 'r') as csvfile:
            documento = open(destino, 'w')
            texto = u'identificacion|area|areaCodigo|fechaGrado|fechaRegistro|ies|nivel|nombreClasificacion|nombreTitulo|numeroRegistro|observacion|subarea|subareaCodigo|tipoExtranjeroColegio|tipoNivel|tipoTitulo\n'
            documento.write(texto)
            reader = csv.DictReader(csvfile)
            index = 1
            for row in reader:
                titulos = consultar_titulos_senescyt(row['cedula'], force=False)

                print('consultando senescyt', index, row['cedula'], titulos)

                if titulos is not None and 'niveltitulos' in titulos:
                    for item in titulos['niveltitulos']:
                        for subitem in item['titulo']:
                            texto = u'%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (
                                row['cedula'],
                                getVal(subitem, 'area'),
                                getVal(subitem, 'areaCodigo'),
                                getVal(subitem, 'fechaGrado'),
                                getVal(subitem, 'fechaRegistro'),
                                getVal(subitem, 'ies'),
                                getVal(subitem, 'nivel'),
                                getVal(subitem, 'nombreClasificacion'),
                                getVal(subitem, 'nombreTitulo'),
                                getVal(subitem, 'numeroRegistro'),
                                getVal(subitem, 'observacion'),
                                getVal(subitem, 'subarea'),
                                getVal(subitem, 'subareaCodigo'),
                                getVal(subitem, 'tipoExtranjeroColegio'),
                                getVal(subitem, 'tipoNivel'),
                                getVal(subitem, 'tipoTitulo'),
                            )
                            documento.write(texto)
                index = index + 1

            documento.close()

            return errores_rc
    except Exception as e:
        log.error('Error al exportar titulos %s', e)
    return None


def consultar_datos_conadis_all(archivo, archivo_resultado):
    """
    @autor: Danny Muñoz
    @fecha: 2018-06-08
    Recibe un archivo csv la cual contiene la cedula de un estudiante en donde se envia a consultar al ws del discapcidad
    la cual consulta si es discapacitado, si lo es se agrega los datos del estudiante con discapacidad a otro archivo resultado.
    Si no encuentra nada escribe una línea solo con la cédula para mantener la misma districuón del archivo original
    """
    try:
        with open(archivo, 'r') as csvfile:
            documento = open(archivo_resultado, 'w')
            texto = u'cedula|codigoConadis|GradoDiscapacidad|PorcentajeDiscapacidad|DeficienciaPredomina|FechaConadis\n'
            documento.write(texto)
            reader = csv.DictReader(csvfile)
            index = 1
            for row in reader:
                result = consultar_discapacidad_msp(row['cedula'], force=False)
                print('consultando', index, row['cedula'], result)

                documento.write(row['cedula'])

                if result is not None and 'Mensaje' not in result:
                    print(index, 'Estudiante Discapacitado', row['cedula'])
                    fechaConadis = ''

                    if 'FechaConadis' in result:
                        fechaConadis = result['FechaConadis']

                    texto = u'|%s|%s|%s|%s|%s' % (
                        result['CodigoConadis'],
                        result['GradoDiscapacidad'],
                        result['PorcentajeDiscapacidad'],
                        result['DeficienciaPredomina'],
                        fechaConadis)

                    documento.write(texto)

                documento.write('\n')
                index = index + 1

            documento.close()
    except Exception as e:
        log.error('Error al exportar datos conadis %s', e)
    return None


def actualizar_datos_funcionarios_bsg_all(cedulas=None, force=False, debug=False):
    """
    @autor: Danny Muñoz
    @fecha: 2018-10-17
    Actualiza todos los datos de los funcionarios con los servicios BSG
    """
    try:
        if cedulas:
            aceds = cedulas.replace(" ", "").split(',')
            lista = Funcionario.objects.filter(usuario__persona__numero_documento__in=aceds).all()
        else:
            lista = Funcionario.objects.all()
        i = 0
        for funcionario in lista:
            i = i + 1
            persona = funcionario.usuario.persona
            print('Actualizando...%s - ide: %s' % (i, persona.numero_documento))
            persona.actualizar_datos_bsg(debug=debug, force=force)
        print(u'Actualuizados:...............  %s', len(lista))
    except Exception as e:
        print('Error al exportar actualizar_datos_funcionarios_bsg_all %s', e)
