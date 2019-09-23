from datetime import datetime
from _decimal import Decimal

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



"""@receiver(post_save, sender=CuentaCobrar)
def cuentacobrar_postsave_handler(sender, instance, **kwargs):

    if kwargs["created"]:
        fecha_actual = datetime.now()

        fecha_emision = instance.fecha_emision


        tasa_interes = TasaInteres.objects.all()

        for tasa in tasa_interes:
            interes_mensual = InteresMensual()
            if int(tasa.anio) >= int(fecha_emision.year) and int(tasa.mes) >= int(fecha_emision.month) \
                    and int(tasa.anio) <= int(fecha_actual.year) and int(tasa.mes) <= int(fecha_actual.month):
                interes = (instance.monto * tasa.tasa) / 100

                #interes_total = Decimal(interes_total) + Decimal(interes)

                #saldo = monto + interes_total

                interes_mensual.cuenta_cobrar = instance
                interes_mensual.tasa = tasa
                interes_mensual.fecha = datetime(int(tasa.anio), int(tasa.mes), 1).date()
                interes_mensual.valor = Decimal(round(interes, 2))

                try:
                    interes_mensual.save()

                except NameError:
                    hh = 'Solicitud incorrecta'

        return render('tesoreria/cuenta_cobrar/lista.html', locals())


"""""