from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import *

class CantonAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_th', 'codigo_inec', 'provincia')
    list_filter = ('provincia',)
    search_fields = ('nombre', 'provincia__nombre')
    list_editable = ('codigo_th', 'codigo_inec')


class CatalagoItemInline(admin.TabularInline):
    model = CatalogoItem
    extra = 1


class CatalagoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion', 'version')
    inlines = [CatalagoItemInline]


class CatalagoItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_th', 'codigo_sg', 'catalogo')
    list_filter = ('catalogo',)
    search_fields = ('nombre', 'catalogo__codigo')
    list_editable = ('codigo_th', 'codigo_sg')


class InstitucionEducativaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'parroquia')
    list_filter = ('parroquia__canton__provincia', 'parroquia__canton')
    search_fields = ('nombre',)


class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_th', 'codigo_inec', 'canton')
    list_filter = ('canton__provincia', 'canton')
    search_fields = ('canton__nombre',)
    list_editable = ('codigo_th', 'codigo_inec')


class PersonaAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'primer_apellido', 'segundo_apellido', 'primer_nombre', 'segundo_nombre')
    search_fields = ('numero_documento', 'primer_apellido', 'segundo_apellido', 'primer_nombre', 'segundo_nombre')


class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_th', 'codigo_inec', 'pais')
    list_filter = ('pais',)
    search_fields = ('nombre',)
    list_editable = ('codigo_th', 'codigo_inec')


class PeriodoFiscalAdmin(admin.ModelAdmin):
    fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'activo')
    search_fields = ('nombre',)
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin')
    list_display_links = ('nombre',)
    list_per_page = 10
    ordering = ('fecha_inicio',)


admin.site.register(Campus)
admin.site.register(Canton, CantonAdmin)
admin.site.register(Catalogo, CatalagoAdmin)
admin.site.register(CatalogoItem, CatalagoItemAdmin)
admin.site.register(IES)
admin.site.register(InsitucionEducativa, InstitucionEducativaAdmin)
admin.site.register(Pais)
admin.site.register(Parroquia, ParroquiaAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(PeriodoFiscal, PeriodoFiscalAdmin)
admin.site.register(Permission)
admin.site.register(Sede)
