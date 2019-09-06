# Create your tasks her
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db.models import Q
from datetime import date
from .models import AutoridadProgramaEstudio
from .models import AutoridadFacultad


@shared_task
def actualizar_autoridad_academica():
    """
    tarea para inactivar autoridades fuera del rango de sus fechas
    Autoridades progrmaa estudio llamo al metodo save para que
    se llame el signal post_update y se quiten sus permisos.
    :return:
    """
    hoy = date.today()
    data = {"activo": False}
    auts = AutoridadProgramaEstudio.objects.filter(Q(activo=True) & Q(Q(fecha_fin__lt=hoy) | Q(fecha_inicio__gt=hoy)))
    for a in auts.all():
        a.activo=False
        a.save()
    AutoridadFacultad.objects.filter(Q(activo=True) & Q(Q(fecha_fin__lt=hoy) | Q(fecha_inicio__gt=hoy))).update(**data)

