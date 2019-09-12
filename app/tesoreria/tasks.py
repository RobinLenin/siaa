# Create your tasks her
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db.models import Q
from datetime import date
from .models import CuentaCobrar

@shared_task
def calcular_interes_mensual():

    hoy = date.today()
    auts = CuentaCobrar.objects.filter(Q(activo=True))
    for a in auts.all():
        a.interes=False
        a.save()
    #AutoridadFacultad.objects.filter(Q(activo=True) & Q(Q(fecha_fin__lt=hoy) | Q(fecha_inicio__gt=hoy))).update(**data)

