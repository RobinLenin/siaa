from django.contrib import admin

from .models import *

__author__ = 'JJM'

""" CURRICULAR MODELS """


class CampoFormacionInline(admin.TabularInline):
    model = CampoFormacion
    extra = 0


class CampoFormacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('nivel_formacion', 'nivel_formacion__regimen',)
    search_fields = ('nombre',)


class ComponenteAprendizajeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    list_filter = ('regimen',)


class OrganizacionCurricularInline(admin.TabularInline):
    model = OrganizacionCurricular
    extra = 0


class OrganizacionCurricularAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    list_filter = ('nivel_formacion', 'nivel_formacion__regimen',)
    search_fields = ('nombre',)


class TipoFormacionInline(admin.TabularInline):
    model = TipoFormacion
    extra = 0


class TipoFormacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel_formacion',)
    list_filter = ('nivel_formacion', 'nivel_formacion__regimen',)
    search_fields = ('nombre',)


class NivelFormacionAdmin(admin.ModelAdmin):
    list_display = ('estado', 'nombre',)
    list_filter = ('regimen',)
    search_fields = ('nombre',)
    inlines = [CampoFormacionInline, TipoFormacionInline, OrganizacionCurricularInline]


""" UNESCO MODELS """


class CampoDetalladoInline(admin.TabularInline):
    model = CampoDetallado
    extra = 1


class CampoDetalladoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'campo_especifico')
    list_filter = ('campo_especifico', 'campo_especifico__campo_amplio')


class CampoEspecificoInline(admin.TabularInline):
    model = CampoEspecifico
    extra = 1


class CampoEspecificoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'campo_amplio')
    list_filter = ('campo_amplio',)
    inlines = [CampoDetalladoInline]


class CampoAmplioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    inlines = [CampoEspecificoInline]


admin.site.register(CampoFormacion, CampoFormacionAdmin)
admin.site.register(ComponenteAprendizaje, ComponenteAprendizajeAdmin)
admin.site.register(NivelFormacion, NivelFormacionAdmin)
admin.site.register(OrganizacionCurricular, OrganizacionCurricularAdmin)
admin.site.register(TipoFormacion, TipoFormacionAdmin)

admin.site.register(CampoAmplio, CampoAmplioAdmin)
admin.site.register(CampoDetallado, CampoDetalladoAdmin)
admin.site.register(CampoEspecifico, CampoEspecificoAdmin)
