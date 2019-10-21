import calendar
from _decimal import Decimal

from app.tesoreria.models import InteresMensual


class CuentaCobrarAppService:

    @staticmethod
    def get_total_saldo(cuenta_cobrar, fecha):
        intereses_mensuales = InteresMensual.objects.filter(cuenta_cobrar=cuenta_cobrar)
        interes = 0.0
        dias_interes = 0.0
        for interesmensual in intereses_mensuales:
            if interesmensual.fecha_fin.year <= fecha.year and interesmensual.fecha_fin.month < fecha.month and interesmensual.pagado == False:
                interes = Decimal(interes) + Decimal(interesmensual.valor)
            if interesmensual.fecha_fin.year == fecha.year and interesmensual.fecha_fin.month == fecha.month:
                if interesmensual.fecha_inicio.day > 1:
                    dia_inicio = interesmensual.fecha_inicio.day
                else:
                    dia_inicio = 0
                dias_mes = calendar.monthrange(fecha.year, fecha.month)[1] - dia_inicio
                dias_interes = (Decimal(interesmensual.valor) / dias_mes) * (fecha.day - dia_inicio)
        total = Decimal(interes) + Decimal(dias_interes) + Decimal(cuenta_cobrar.saldo)
        return total