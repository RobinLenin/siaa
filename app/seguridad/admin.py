from django.contrib import admin

from app.seguridad.models import CuentaCorreo
from app.seguridad.models import Funcionalidad
from app.seguridad.models import FuncionalidadGroup
from app.seguridad.models import Usuario
from app.seguridad.models import GrupoLDAP


class AuditModelAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = str(request.user)
        obj.updated_by = str(request.user)
        obj.save()


class FuncionalidadAdmin(admin.ModelAdmin):
    fields = (
    'nombre', 'formulario', 'orden', 'padre', 'codigo', 'activo', 'mostrar', 'icon', 'descripcion', 'modulo',)
    list_filter = ('modulo', 'activo',)
    search_fields = ('nombre',)
    list_display = ('codigo', 'nombre', 'formulario', 'icon', 'orden', 'padre')
    list_display_links = ('codigo', 'nombre',)
    list_per_page = 25


class FuncionalidadGrupoAdmin(admin.ModelAdmin):
    fields = ('funcionalidad', 'group',)
    search_fields = ('funcionalidad.nombre',)
    list_display = ('funcionalidad', 'group')
    list_per_page = 25


class UsuarioAdmin(admin.ModelAdmin):
    list_filter = ('activo', 'google', 'is_admin', 'ldap', 'force_password', 'groups')
    list_display = ('persona', 'nombre_de_usuario', 'correo_electronico_institucional', 'last_login', 'activo')
    search_fields = (
        'nombre_de_usuario', 'correo_electronico_institucional',
        'persona__numero_documento', 'persona__primer_apellido', 'persona__segundo_apellido', 'persona__primer_nombre',
        'persona__segundo_nombre')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ('nombre_de_usuario', 'correo_electronico_institucional', 'google', 'ldap')


class CuentaCorreoAdmin(admin.ModelAdmin):
    list_filter = ('tipo',)
    list_display = ('numero_documento', 'nombres', 'apellidos', 'email_institucional')
    search_fields = (
        'numero_documento', 'email_institucional',
        'nombres', 'apellidos')

class GrupoLDAPAdmin(admin.ModelAdmin):
    list_filter = ('ldap',)
    list_display = ('nombre', 'descripcion',)
    search_fields = ('nombre',)


admin.site.register(Funcionalidad, FuncionalidadAdmin)
admin.site.register(FuncionalidadGroup, FuncionalidadGrupoAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(CuentaCorreo, CuentaCorreoAdmin)
admin.site.register(GrupoLDAP, GrupoLDAPAdmin)
