from django.contrib import admin

from .models import *


class AsignacionDePuestoAdmin(admin.ModelAdmin):
    list_display = ('uaa', 'puesto', 'funcionario', 'tipo_relacion_laboral')
    list_filter = ('uaa_puesto',)
    search_fields = (
        'uaa_puesto__uaa__nombre', 'uaa_puesto__puesto__denominacion',
        'funcionario__usuario__nombre_de_usuario', 'funcionario__usuario__persona__primer_apellido',
        'funcionario__usuario__persona__segundo_apellido', 'funcionario__usuario__persona__numero_documento')


class GrupoOcupacionalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'grado', 'nivel', 'rmu', 'regimen_laboral')
    list_filter = ('regimen_laboral',)
    search_fields = ('nombre',)


class UAAPuestoAdmin(admin.ModelAdmin):
    list_display = ('uaa', 'puesto', 'activo')
    list_filter = ('uaa',)


class VacacionesAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'dias_totales', 'horas_totales', 'dias_pendientes', 'horas_pendientes')
    search_fields = ('funcionario__usuario__nombre_de_usuario', 'funcionario__usuario__persona__primer_apellido',
                     'funcionario__usuario__persona__segundo_apellido',
                     'funcionario__usuario__persona__numero_documento')


class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'activo')
    search_fields = (
        'usuario__persona__numero_documento', 'usuario__persona__primer_apellido',
        'usuario__persona__segundo_apellido', 'usuario__persona__primer_nombre',
        'usuario__persona__segundo_nombre')


class AusentismoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'tipo_ausentismo', 'descripcion', 'con_remuneracion', 'imputable_vacaciones', 'limite_tiempo',
        'limite_anios', 'limite_meses',
        'limite_dias', 'limite_horas')
    # list_editable = ('tipo_ausentismo',)


class PuestoAdmin(admin.ModelAdmin):
    list_display = ('denominacion', 'anio_clasificacion_puesto', 'ambito_ejecucion', 'area_conocimiento')
    search_fields = ('denominacion',)


admin.site.register(ActividadEsencial)
admin.site.register(Administrativo)
admin.site.register(Trabajador)
admin.site.register(Docente)
admin.site.register(AsignacionPuesto, AsignacionDePuestoAdmin)
admin.site.register(Ausentismo, AusentismoAdmin)
admin.site.register(AusentismoFuncionario)
admin.site.register(Conocimiento)
admin.site.register(Destreza)
admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(GrupoOcupacional, GrupoOcupacionalAdmin)
admin.site.register(Puesto, PuestoAdmin)
admin.site.register(RegimenLaboral)
admin.site.register(RegistroVacaciones)
admin.site.register(UAAPuesto, UAAPuestoAdmin)
admin.site.register(Vacaciones, VacacionesAdmin)
admin.site.register(PeriodoVacaciones)
admin.site.register(CompensacionDias)
admin.site.register(PeriodoVacionesRelacionLaboral)
