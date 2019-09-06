import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta


def fecha_mayor(fecha1, fecha2):
    """
    Devulve la fecha mayor entre las dos, si alguna es null devuelve la otra
    :param fecha1:
    :param fecha2:
    :return:
    """
    if fecha1 and fecha1 > fecha2:
        return fecha1
    return fecha2 if fecha2 else fecha1


def fecha_menor(fecha1, fecha2):
    """
    Devulve la fecha menor entre las dos, si alguna es null devuelve la otra
    :param fecha1:
    :param fecha2:
    :return:
    """
    if fecha1 and fecha2 and fecha1 < fecha2:
        return fecha1
    return fecha2 if fecha2 else fecha1


def diferencia(fecha_inicial, fecha_final):
    """
    Devuelve los dias , meses y años de diferencia entre fechas
    :param fecha_inicial: Fecha inicial, debe ser menor a la final, caso contrario devuelve negativo
    :param fecha_final: Fecha final
    :return: {dias, meses, anios }
    """
    r = relativedelta(fecha_final, fecha_inicial)
    return {'dias': r.days,
            'meses': r.months,
            'anios': r.years}


def diferencia_dias(fecha_inicial, fecha_final):
    """
    Devuelve el total de dias entre dos fechas
    :param fecha_inicial: Fecha inicial, debe ser menor a la final, caso contrario devuelve negativo
    :param fecha_final: Fecha final
    :return:
    """
    return (fecha_final - fecha_inicial).days


def diferencia_meses(fecha_inicial, fecha_final):
    """
    Devuelve el total de meses entre dos fechas
    :param fecha_inicial: Fecha inicial, debe ser menor a la final, caso contrario devuelve 0
    :param fecha_final: Fecha final
    :return:
    """
    meses = 0
    while True:
        dias_mes = monthrange(fecha_inicial.year, fecha_inicial.month)[1]
        fecha_inicial += datetime.timedelta(days=dias_mes)
        if fecha_inicial <= fecha_final:
            meses += 1
        else:
            break
    return meses

def calcular_edad(fecha_nacimiento):
    """
    Calcula la edad de acuerdo a una fecha de nacimiento de tipo fecha
    :param fecha_nacimiento: Tipo fecha
    :return:
    """
    if not fecha_nacimiento:
        return None

    fecha = fecha_nacimiento.year
    hoy = datetime.date.today().year

    if datetime.date.today().month > fecha_nacimiento.month:
        return hoy - fecha
    else:
        if datetime.date.today().month == fecha_nacimiento.month:
            if datetime.date.today().day >= fecha_nacimiento.day:
                return hoy - fecha
            else:
                return hoy - fecha - 1
        else:
            return hoy - fecha - 1
