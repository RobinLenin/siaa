import calendar
import datetime
from _decimal import Decimal
from django.utils.dateparse import parse_date

from app.tesoreria.models import InteresMensual, CuentaCobrar, TasaInteres


class CuentaCobrarAppService:

    @staticmethod
    def get_total_saldo(cuenta_cobrar, fecha):
        intereses_mensuales = InteresMensual.objects.filter(cuenta_cobrar=cuenta_cobrar)
        interes = 0.0
        dias_interes = 0.0
        for interesmensual in intereses_mensuales:
            if (interesmensual.fecha_fin.year <= fecha.year) and (interesmensual.fecha_fin.month < fecha.month) and (interesmensual.pagado == False):
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

    @staticmethod
    def recalculo(request):
        id_cli = request.POST.get('cuenta_cobrar')
        cuenta_cobrar = CuentaCobrar.objects.get(id=str(id_cli))
        saldo_aux = cuenta_cobrar.saldo
        pagado = request.POST.get('monto')
        interes_cc_aux = cuenta_cobrar.interes
        fecha_pago_str = request.POST.get('fecha_pago')
        monto = request.POST.get('monto')
        fecha_pago = parse_date(fecha_pago_str)
        diferencia_dias = 0
        interes_dias = 0.00
        interes_dias_aux = 0.00

        try:
            interes_mensual = InteresMensual.objects.get(cuenta_cobrar=cuenta_cobrar,
                                                         fecha_fin__year=fecha_pago.year,
                                                         fecha_fin__month=fecha_pago.month)
        except interes_mensual.DoesNotExist:
            interes_mensual = None

        try:
            intereses_mensuales = InteresMensual.objects.filter(cuenta_cobrar=cuenta_cobrar,
                                                                fecha_fin__gt=fecha_pago).order_by('fecha_fin')
        except intereses_mensuales.DoesNotExist:
            intereses_mensuales = None

        try:
            intereses_mensuales_menores = InteresMensual.objects.filter(cuenta_cobrar=cuenta_cobrar,
                                                                        fecha_fin__lte=fecha_pago).order_by('fecha_fin')
        except intereses_mensuales_menores.DoesNotExist:
            intereses_mensuales_menores = None

        if intereses_mensuales_menores != None:

            for interesmensual in intereses_mensuales_menores:
                if Decimal(pagado) >= Decimal(interesmensual.valor):
                    InteresMensual.objects.values('pagado').filter(id=interesmensual.id).update(pagado=True)
                    pagado = Decimal(pagado) - Decimal(interesmensual.valor)

        if intereses_mensuales != None:
            print("Saldo 1no cuenta", saldo_aux)
            for interesmensual in intereses_mensuales:
                print("fOR")
                print("interes mensual valor ", interesmensual.valor)
                print("interes cuenta ", interes_cc_aux)

                interes_cc_aux = Decimal(interes_cc_aux) - Decimal(interesmensual.valor)
            print("interes cuenta aux", interes_cc_aux)

        if not interes_mensual == None:

            dias = fecha_pago.day
            print("dia pago", dias)
            diferencia_dias = calendar.monthrange(interes_mensual.tasa.anio, interes_mensual.tasa.mes)[
                                  1] - dias
            interes_dias = (((Decimal(saldo_aux) * Decimal(interes_mensual.tasa.tasa)) / 100) /
                            calendar.monthrange(interes_mensual.tasa.anio, interes_mensual.tasa.mes)[
                                1]) * dias
            print("interes primeros dias ", interes_dias)
            print("saldo cuenta ", saldo_aux)
            if Decimal(monto) > Decimal(interes_dias + interes_cc_aux):
                diferencia_saldo = Decimal(monto) - Decimal(interes_dias + interes_cc_aux)
                print("monto.abono menos interes primeros dias ", diferencia_saldo)
                # diferencia_saldo = Decimal(diferencia_saldo) - Decimal(interes_cc_aux)
                saldo_aux = Decimal(saldo_aux) - Decimal(diferencia_saldo)
                interes_dias_aux = Decimal(interes_cc_aux) + Decimal(interes_dias)
                interes_cc_aux = 0
                print("saldo cuenta luego de abonar", saldo_aux)

            else:
                interes_cc_aux = Decimal(interes_dias + interes_cc_aux) - Decimal(monto)
                interes_dias_aux = monto

            interes_dias_diferencia = (((Decimal(saldo_aux) * Decimal(interes_mensual.tasa.tasa)) / 100) /
                                       calendar.monthrange(interes_mensual.tasa.anio, interes_mensual.tasa.mes)[
                                           1]) * diferencia_dias
            suma_interes = interes_dias + interes_dias_diferencia
            print("interes mes pagado", suma_interes)
            print("interes cuenta ", interes_cc_aux)
            # interes_cc_aux = Decimal(interes_dias_diferencia)
            interes_cc_aux = Decimal(suma_interes) + Decimal(interes_cc_aux)
            print("interes cuenta ", interes_cc_aux)
            print(interes_dias)
            interes_cc_aux = round(interes_cc_aux, 2)
            print("saldo cuenta ", saldo_aux)

            fecha_pago_abono = datetime.datetime.strptime(request.POST.get('fecha_pago'), '%Y-%m-%d')
            saldo_total = CuentaCobrarAppService.get_total_saldo(cuenta_cobrar, fecha_pago_abono)
            print("MONTO;", monto)
            print("Saldo Total:", round(saldo_total, 2))
            if Decimal(monto) == Decimal(round(saldo_total, 2)):
                boll = 0
                print("MONTO;", monto)
                print("Saldo Total:", saldo_total)
                fecha_cancelacion = datetime.datetime.now()
                CuentaCobrar.objects.values('estado', 'fecha_cancelacion', 'interes', 'saldo').filter(id=id_cli).update(
                    estado=False,
                    fecha_cancelacion=fecha_cancelacion, interes=boll, saldo=boll)
            else:
                boll = 1
                CuentaCobrar.objects.values('interes', 'saldo').filter(id=id_cli).update(interes=interes_cc_aux,
                                                                                         saldo=saldo_aux)

            InteresMensual.objects.values('valor').filter(id=interes_mensual.id).update(valor=suma_interes)

            saldo = saldo_aux
            interes = Decimal(interes_cc_aux)

            print("AAAAAAAAAAAAAAAAAAAAAAAAAA", interes_cc_aux)

            for interesmensual in intereses_mensuales:
                if interesmensual.id != interes_mensual.id:
                    interes_mes = (saldo * interesmensual.tasa.tasa) / 100
                    interes = interes + interes_mes
                    print("interes mes ", interes_mes)
                    print("interes cuenta ", interes)
                    InteresMensual.objects.values('valor').filter(id=interesmensual.id).update(valor=interes_mes)

            interes_cambio = interes * boll

            CuentaCobrar.objects.values('interes').filter(id=id_cli).update(interes=interes_cambio)

        return Decimal(interes_dias_aux)
        pass

    @staticmethod
    def calcular_saldo(monto, anio, mes, dia):
        fecha_actual = datetime.datetime.now()
        interes_total = 0.00
        tasa_interes = TasaInteres.objects.all()
        diferencia_dias = calendar.monthrange(anio, mes)[1] - dia
        for tasa in tasa_interes:

            if int(tasa.anio) >= anio and int(tasa.mes) >= mes \
                    and int(tasa.anio) <= int(fecha_actual.year) and int(tasa.mes) <= int(fecha_actual.month):
                interes = (monto * tasa.tasa) / 100
                if dia > 1:
                    interes = (((monto * tasa.tasa) / 100) /
                               calendar.monthrange(anio, mes)[
                                   1]) * diferencia_dias
                print(interes)
                interes_total = Decimal(interes_total) + Decimal(interes)
                dia = 0
        return interes_total

    @staticmethod
    def validar_tasa_interes(anio, mes):
        val = True
        tasa_interes = TasaInteres.objects.all()
        for tasa in tasa_interes:
            print(tasa.anio, tasa.mes)
            if str(tasa.anio) == str(anio) and str(tasa.mes) == str(mes):
                val = False

        return val