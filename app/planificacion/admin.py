from django.contrib import admin

from .models import *

__author__ = 'JJM'

""" PEDI MODELS """

class ObjetivoEstrategicoInline(admin.TabularInline):
    model = ObjetivoEstrategico
    extra = 0

class ObjetivoOperativoInline(admin.TabularInline):
    model = ObjetivoOperativo
    extra = 0

class PoliticaInline(admin.TabularInline):
    model = Politica
    extra = 0

class EstrategiaInline(admin.TabularInline):
    model = Estrategia
    extra = 0


class ResultadoInline(admin.TabularInline):
    model = Resultado
    extra = 0

class IndicadorInline(admin.TabularInline):
    model = Indicador
    extra = 0

class MetaAnualInline(admin.TabularInline):
    model = MetaAnual
    extra = 0

class ActividadInline(admin.TabularInline):
    model = Actividad
    extra = 0

class VerificacionInline(admin.TabularInline):
    model = Verificacion
    extra = 0

class PlanEstrategicoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('activo', 'periodos',)
    search_fields = ('nombre',)
    inlines = [ObjetivoEstrategicoInline, PoliticaInline, EstrategiaInline]


class ObjetivoEstrategicoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('activo', 'plan_estrategico',)
    search_fields = ('nombre',)
    inlines = [ObjetivoOperativoInline]


class ObjetivoOperativoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('activo', 'objetivo_estrategico__plan_estrategico', 'objetivo_estrategico',)
    search_fields = ('nombre',)
    inlines = [ResultadoInline]


class PoliticaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('plan_estrategico', )
    search_fields = ('nombre',)


class EstrategiaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('plan_estrategico', )
    search_fields = ('nombre',)

class ResultadoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('objetivo_operativo', )
    search_fields = ('nombre',)
    inlines = [IndicadorInline]


class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('resultado',
    'resultado__objetivo_operativo__objetivo_estrategico__plan_estrategico', 'resultado__objetivo_operativo__objetivo_estrategico',
    )
    search_fields = ('meta_nombre', 'nombre',)
    inlines = [MetaAnualInline]

class MetaAnualAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('periodo',
    'indicador__resultado__objetivo_operativo__objetivo_estrategico__plan_estrategico', 'indicador__resultado__objetivo_operativo__objetivo_estrategico',
    'indicador__resultado__objetivo_operativo',)
    search_fields = ('activo', 'nombre',)
    inlines = [ActividadInline]


"""
POA MODELS
"""
class PlanOperativoAdmin(admin.ModelAdmin):
    list_display = ('periodo',)
    list_filter = ('periodo', 'plan_estrategico', 'activo')
    search_fields = ('periodo',)

class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('meta_anual__periodo', 'meta_anual__indicador', )
    search_fields = ('nombre',)
    inlines = [VerificacionInline]

class VerificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('actividad__meta_anual', 'actividad__meta_anual__periodo',  'actividad__meta_anual__indicador', )
    search_fields = ('nombre',)

class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'valor',)
    list_filter = ( 'actividad__meta_anual', 'actividad__meta_anual__periodo', 'actividad__meta_anual__indicador', )



admin.site.register(PlanEstrategico, PlanEstrategicoAdmin)
admin.site.register(ObjetivoEstrategico, ObjetivoEstrategicoAdmin)
admin.site.register(ObjetivoOperativo, ObjetivoOperativoAdmin)
admin.site.register(Politica, PoliticaAdmin)
admin.site.register(Estrategia, EstrategiaAdmin)
admin.site.register(Resultado, ResultadoAdmin)
admin.site.register(Indicador, IndicadorAdmin)
admin.site.register(MetaAnual, MetaAnualAdmin)

"""
POA MODELS
"""
admin.site.register(PlanOperativo, PlanOperativoAdmin)
admin.site.register(Actividad, ActividadAdmin)
admin.site.register(Verificacion, VerificacionAdmin)
admin.site.register(Presupuesto, PresupuestoAdmin)
