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
        tasa_interes = TasaInteres.objects.filter(anio__gte=instance.fecha_emision.year,
                                                  mes__gte=instance.fecha_emision.month,
                                                 anio__lte=fecha_actual.year,
                                                mes__lte=fecha_actual.month)
        # filtrar ver si le afecta a esta cuenta preguntar si hay fecha de cancelacion
        for tasa in tasa_interes:
            interes_mensual = InteresMensual()
            interes = (instance.monto * tasa.tasa) / 100

            # interes_total = Decimal(interes_total) + Decimal(interes)
            # saldo = monto + interes_total

            interes_mensual.cuenta_cobrar = instance
            interes_mensual.tasa = tasa
            interes_mensual.fecha_inicio = datetime(int(tasa.anio), int(tasa.mes), 1).date()
            interes_mensual.fecha_fin = datetime(int(tasa.anio), int(tasa.mes), calendar.monthrange(tasa.anio, tasa.mes)[1]).date()
            interes_mensual.valor = Decimal(round(interes, 2))

            try:
                interes_mensual.save()

            except NameError:
                hh = 'Solicitud incorrecta'
