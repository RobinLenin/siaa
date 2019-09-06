from django.contrib import admin

from .models import *


class DetalleParametrizacionInline(admin.TabularInline):
    model = DetalleParametrizacion
    extra = 1

class ParametrizacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion')
    inlines = [DetalleParametrizacionInline]

class DetallePlanificacionInline(admin.TabularInline):
    model = DetallePlanificacion
    extra = 1

class PlanificacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion')
    inlines = [DetallePlanificacionInline]


admin.site.register(Parametrizacion, ParametrizacionAdmin)
admin.site.register(Planificacion, PlanificacionAdmin)
