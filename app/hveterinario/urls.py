from django.conf.urls import url
from . import views

app_name = 'hveterinario'
urlpatterns = [
    url(r'^$', views.mi_index, name='index'),
    url(r'^propietarios/$', views.registros_paginados_propietarios, name='index'),
    url(r'^pacientes_por_propietario/(\w+)/$', views.registros_paginados_pacientes, name='paciente.lista_pacientes_por_propietario'),
    url(r'^propietario/(\w+)/paciente/$', views.paciente, name='paciente'), #Agregar paciente
    url(r'^propietario/(?P<id_persona>\w+)/paciente/(?P<id_paciente>\w+)/$', views.paciente, name='paciente'), #Editar registro de paciente
    #url(r'^consultas_por_paciente/(?P<id_persona>\w+)/$', views.registros_paginados_consulta_por_paciente, name='consulta.lista_consulta_por_pacientes'),
    url(r'^consultas_por_paciente/(?P<id_paciente>\w+)/$', views.registros_paginados_consulta_por_paciente, name='consulta.lista_consulta_por_pacientes'),
    url(r'^paciente/(?P<id_paciente>\w+)/consulta/$', views.consulta, name='consulta'),
    url(r'^paciente/(?P<id_paciente>\w+)/consulta/(?P<id_consulta>\w+)/$', views.consulta, name='consulta'), #para editar pendiente
    url(r'^consulta_detalle/(?P<id_consulta>\w+)/$', views.consulta_detalle, name='consulta.detalle'),
    url(r'^detalle/anamnesis/(?P<id_consulta>\w+)/$', views.detalles_consulta_anamnesis, name='consulta.detalles.anamnesis'),
    url(r'^detalle/examen_clinico/(?P<id_consulta>\w+)/$', views.detalles_consulta_examen_clinico, name='consulta.detalles.examen.clinico'),
    url(r'^detalle/examen_clinico/datos_Presuntivos/(?P<id_consulta>\w+)/$', views.agregarDatosPresuntivos, name='consulta.detalles.examen.clinico.datos_presuntivos'),
    url(r'^detalle/lista_maestra/(?P<id_consulta>\w+)/$', views.detalles_consulta_lista_maestra, name='consulta.detalles.lista.maestra'),
    url(r'^detalle/diagnostico_diferencial/(?P<id_consulta>\w+)/$', views.detalles_consulta_diagnostico_diferencial, name='consulta.detalles.diagnostico.diferencial'),
    url(r'^detalle/diagnostico_presuntivo/(?P<id_consulta>\w+)/$', views.detalles_consulta_diagnostico_presuntivo, name='consulta.detalles.diagnostico.presuntivo'),
    url(r'^detalle/examenes_complementarios/(?P<id_consulta>\w+)/$', views.detalles_consulta_examenes_complementarios, name='consulta.detalles.examenes.complementarios'),
    url(r'^detalle/diagnostico_final/(?P<id_consulta>\w+)/$', views.detalles_consulta_diagnostico_final, name='consulta.detalles.diagnostico.final'),
    url(r'^detalle/tratamiento/(?P<id_consulta>\w+)/$', views.detalles_consulta_tratamiento, name='consulta.detalles.tratamiento'),
    url(r'^detalle/inscripcion_tratamiento/(?P<id_consulta>\w+)/$', views.detalles_consulta_inscripcion_tratamiento, name='consulta.detalles.inscripcion.tratamiento'),

    
    
    

    #url(r'^paciente/(\w+)/$', views.paciente, name='paciente_agregar.pacientee'),
    
]
