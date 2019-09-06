from django.contrib import admin

from .models import Plantilla
from app.seguridad.admin import AuditModelAdmin


class PlantillaAdmin(AuditModelAdmin):
    fields = ('codigo', 'descripcion', 'definicion', 'updated_by', 'created_by', 'created_at', 'updated_at',)
    search_fields = ('descripcion', 'codigo',)
    list_display = ('codigo', 'descripcion',)


admin.site.register(Plantilla, PlantillaAdmin)
