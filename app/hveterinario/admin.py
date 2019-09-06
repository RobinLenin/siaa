from django.contrib import admin

from app.hveterinario.models import *
# Register your models here.



admin.site.register(Paciente)
admin.site.register(Consulta)
admin.site.register(Anamnesis)
admin.site.register(ExamenClinico)
admin.site.register(DatosPresuntivos)
admin.site.register(ListaMaestra)
admin.site.register(DiagnosticoDiferencial)
admin.site.register(DiagnosticoPresuntivo)
admin.site.register(ExamenesComplementarios)
admin.site.register(DiagnosticoFinal)
admin.site.register(Tratamiento)
admin.site.register(InscripcionTratamiento)

