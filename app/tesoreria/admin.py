from django.contrib import admin

from .models import CuentaCobrar, Abono, TasaInteres, Comentario, InteresMensual

from app.seguridad.admin import AuditModelAdmin


class CuentaCobrarAdmin(admin.ModelAdmin):
    #fields = ('codigo', 'descripcion', 'definicion', 'updated_by', 'created_by', 'created_at', 'updated_at',)
    # search_fields = ('concepto', 'cliente',)
    list_display = ('concepto', 'cliente',)
    raw_id_fields = ('cliente',)

class AbonoAdmin(admin.ModelAdmin):
    #fields = ('codigo', 'descripcion', 'definicion', 'updated_by', 'created_by', 'created_at', 'updated_at',)
    #search_fields = ('descripcion', 'codigo',)
    list_display = ('concepto', 'monto',)
    #raw_id_fields = ('cliente',)

class ComentarioAdmin(admin.ModelAdmin):
    #fields = ('codigo', 'descripcion', 'definicion', 'updated_by', 'created_by', 'created_at', 'updated_at',)
    #search_fields = ('descripcion', 'codigo',)
    list_display = ('fecha_creacion', 'concepto',)
    #raw_id_fields = ('cliente',)


class TasaInteresAdmin(admin.ModelAdmin):
    #fields = ('codigo', 'descripcion', 'definicion', 'updated_by', 'created_by', 'created_at', 'updated_at',)
    #search_fields = ('descripcion', 'codigo',)
    list_display = ('anio', 'mes', 'tasa',)
    #raw_id_fields = ('cliente',)

class InteresMensualAdmin(admin.ModelAdmin):
    # fields = ('codigo', 'descripcion', 'definicion', 'updated_by', 'created_by', 'created_at', 'updated_at',)
    # search_fields = ('descripcion', 'codigo',)
    list_display = ('fecha_inicio','fecha_fin', 'valor', 'tasa',)
    # raw_id_fields = ('cliente',)

admin.site.register(CuentaCobrar, CuentaCobrarAdmin)
admin.site.register(Abono, AbonoAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(TasaInteres, TasaInteresAdmin)
admin.site.register(InteresMensual, InteresMensualAdmin)

