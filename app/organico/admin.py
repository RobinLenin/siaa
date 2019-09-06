from django.contrib import admin

from app.organico.models import UAA


class UAAAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    list_display = ('nombre', 'uaa', 'codigo', 'estructura_organizacional', 'academico', 'administrativo')
    list_editable = ('codigo',)
    list_filter = ('uaa',)


admin.site.register(UAA, UAAAdmin)
