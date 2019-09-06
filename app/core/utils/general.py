from django.core.paginator import Paginator


def api_paginacion(queryset, page=None, numero_items_por_pagina=None):
    """
    Retorna lista de objetos segun la paginación requerida
    :param queryset: sql del ORM a ejecutar
    :param page: número de página
    :param numero_items_por_pagina: número de objetos a retornar
    :return: lista de objetos
    """
    try:
        paginator = Paginator(queryset, numero_items_por_pagina)
        queryset = paginator.page(page)
    except Exception as e:
        print(e)
    return queryset


def verificar_ci(numero_documento):
    """
    Determina el tipo de documento y lo valida
    :param numero_documento:
    :return:
    """
    if len(numero_documento) == 10 or len(numero_documento) == 13:  # verificar la longitud correcta
        cp = int(numero_documento[0:2])
        # verificar codigo de provincia (01-24 y 30=registrados en el exterior)
        if (cp >= 1 and cp <= 24) or cp == 30:
            tercer_dig = int(numero_documento[2])
            if tercer_dig >= 0 and tercer_dig < 6:  # numeros enter 0 y 6
                if len(numero_documento) == 10:
                    return validar_ced_ruc(numero_documento, 0)
                elif len(numero_documento) == 13:
                    # se verifica q los ultimos numeros no sean 000
                    return validar_ced_ruc(numero_documento, 0) and numero_documento[10:13] != '000'
            elif tercer_dig == 6:
                return validar_ced_ruc(numero_documento, 1)  # sociedades publicas
            elif tercer_dig == 9:  # si es ruc
                return validar_ced_ruc(numero_documento, 2)  # sociedades privadas
            else:
                raise Exception(u'Tercer digito invalido')
        else:
            raise Exception(u'Codigo de provincia incorrecto')
    else:
        raise Exception(u'Longitud incorrecta del numero ingresado')

def validar_ced_ruc(numero_documento, tipo):
    """
    Valida el numero de documento de acuerdo a su tipo
    :param numero_documento:
    :param tipo:
    :return:
    """
    total = 0
    if tipo == 0:  # cedula y r.u.c persona natural
        base = 10
        d_ver = int(numero_documento[9])  # digito verificador
        multip = (2, 1, 2, 1, 2, 1, 2, 1, 2)
    elif tipo == 1:  # r.u.c. publicos
        base = 11
        d_ver = int(numero_documento[8])
        multip = (3, 2, 7, 6, 5, 4, 3, 2)
    elif tipo == 2:  # r.u.c. juridicos y extranjeros sin cedula
        base = 11
        d_ver = int(numero_documento[9])
        multip = (4, 3, 2, 7, 6, 5, 4, 3, 2)
    for i in range(0, len(multip)):
        p = int(numero_documento[i]) * multip[i]
        if tipo == 0:
            total += p if p < 10 else int(str(p)[0]) + int(str(p)[1])
        else:
            total += p
    mod = total % base
    val = base - mod if mod != 0 else 0
    return val == d_ver


def dividir_nombres_completos(nombres):
    """
    Divide el texto, en un arreglo de 2 apellidos y 2 nombres
    :param nombres: 'primer_apellido,segundo_apellido,primer_nombre,segundo_nombre'
    :return: [primer_apellido,segundo_apellido,primer_nombre,segundo_nombre]
    """
    concatenadores = ["de", "del", "la", "las", "los", "san", "mac", "mc", "van", "von", "y", "i"]
    compuesto = ''
    nueva_cadena = ''

    for i in nombres.split(' '):
        if i.lower() in concatenadores:
            compuesto = compuesto + i + ' '
        else:
            if nueva_cadena == '':
                nueva_cadena = compuesto + i
            else:
                nueva_cadena = nueva_cadena + '|' + compuesto + i
            compuesto = ''

    nueva_cadena = nueva_cadena.split('|')
    segundo_nombre = ''
    segundo_apellido = ''

    if len(nueva_cadena) >= 3:
        primer_apellido = nueva_cadena[0]
        segundo_apellido = nueva_cadena[1]
        primer_nombre = nueva_cadena[2]
        segundo_nombre = nombres.replace(primer_apellido, '').replace(segundo_apellido,
                                                                      '').replace(
            primer_nombre, '').strip()
    else:
        primer_apellido = nueva_cadena[0]
        primer_nombre = nueva_cadena[1]

    return [primer_apellido.capitalize(),
            segundo_apellido.capitalize(),
            primer_nombre.capitalize(),
            segundo_nombre.capitalize()]


def dividir_nombres_o_apellidos(nombres=None):
    """
    Divide el texto, en un arreglo de 2 nombres o 2 apellidos
    :param nombres: 'primer_nombre segundo_nombre o primer_apellido segundo_apellido'
    :return: [primer_nombre,segundo_nombre] o [primer_apellido, segundo_apellido]
    """
    concatenadores = ["de", "del", "la", "las", "los", "san", "mac", "mc", "van", "von", "y", "i"]
    compuesto = ''
    nueva_cadena = ''

    for i in nombres.split(' '):
        if i.lower() in concatenadores:
            compuesto = compuesto + i + ' '
        else:
            if nueva_cadena == '':
                nueva_cadena = compuesto + i
            else:
                nueva_cadena = nueva_cadena + '|' + compuesto + i
            compuesto = ''
    nueva_cadena = nueva_cadena.split('|')

    if len(nueva_cadena) >= 1:
        primer_nombre = nueva_cadena[0]
        segundo_nombre = nombres.replace(primer_nombre, '').strip()
    else:
        primer_nombre = nombres[0]
        segundo_nombre = nombres[1]

    return [primer_nombre, segundo_nombre]
