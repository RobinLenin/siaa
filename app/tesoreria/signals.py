from datetime import datetime
from _decimal import Decimal
import calendar


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from app.tesoreria.models import Abono
from app.tesoreria.models import CuentaCobrar
from app.tesoreria.models import InteresMensual
from app.tesoreria.models import TasaInteres


@receiver(post_save, sender=Abono)
def abono_postsave_handler(sender, instance, **kwargs):
    if kwargs["created"]:
        pass
    # instance.cuentacobrar metodo de calcular


@receiver(post_save, sender=CuentaCobrar)
def cuentacobrar_postsave_handler(sender, instance, **kwargs):
    if kwargs["created"]:
        fecha_actual = datetime.now()
        dia_fecha_emision = instance.fecha_emision.day
        tasa_interes = TasaInteres.objects.filter(anio__gte=instance.fecha_emision.year,
                                                  mes__gte=instance.fecha_emision.month,
                                                 anio__lte=fecha_actual.year,
                                                mes__lte=fecha_actual.month).order_by('anio', 'mes')
        # filtrar ver si le afecta a esta cuenta preguntar si hay fecha de cancelacion




        for tasa in tasa_interes:


            interes_mensual = InteresMensual()
            interes = (instance.monto * tasa.tasa) / 100

            if dia_fecha_emision > 1:
                diferencia_dias = calendar.monthrange(instance.fecha_emision.year, instance.fecha_emision.month)[
                                  1] - dia_fecha_emision
                interes = (((Decimal(instance.monto) * Decimal(tasa.tasa)) / 100) /
                            calendar.monthrange(instance.fecha_emision.year, instance.fecha_emision.month)[
                                1]) * diferencia_dias
            interes_mensual.cuenta_cobrar = instance
            interes_mensual.tasa = tasa
            interes_mensual.pagado = False
            interes_mensual.fecha_inicio = datetime(year=int(tasa.anio), month=int(tasa.mes), day=int(dia_fecha_emision))
            interes_mensual.fecha_fin = datetime(int(tasa.anio), int(tasa.mes), calendar.monthrange(tasa.anio, tasa.mes)[1]).date()
            interes_mensual.valor = Decimal(round(interes, 2))

            try:
                interes_mensual.save()

            except NameError:
                hh = 'Solicitud incorrecta'

            dia_fecha_emision = 1