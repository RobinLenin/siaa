from django.urls import path

from app.academico.views import views_curricular

urlpatterns = [
    path('curricular', views_curricular.index_curricular, name='index_curricular'),

    path('asignatura-componente/guardar', views_curricular.asignatura_componente_guardar, name='asignatura_componente_guardar'),

    path('asignatura-nivel/detalle/<int:id>', views_curricular.asignatura_nivel_detalle, name='asignatura_nivel_detalle'),
    path('asignatura-nivel/eliminar/<int:id>', views_curricular.asignatura_nivel_eliminar, name='asignatura_nivel_eliminar'),
    path('asignatura-nivel/guardar', views_curricular.asignatura_nivel_guardar, name='asignatura_nivel_guardar'),
    path('asignatura-nivel/guardar/prerrequisito', views_curricular.asignatura_nivel_guardar_prerrequisito, name='asignatura_nivel_guardar_prerrequisito'),
    path('asignatura-nivel/guardar/correquisito', views_curricular.asignatura_nivel_guardar_correquisito, name='asignatura_nivel_guardar_correquisito'),

    path('asignatura/detalle/<int:id>', views_curricular.asignatura_detalle, name='asignatura_detalle'),
    path('asignatura/eliminar/<int:id>', views_curricular.asignatura_eliminar, name='asignatura_eliminar'),
    path('asignatura/guardar', views_curricular.asignatura_guardar, name='asignatura_guardar'),
    path('asignatura/lista', views_curricular.asignatura_lista, name='asignatura_lista'),
    path('asignatura/lista-paginador', views_curricular.asignatura_lista_paginador, name='asignatura_lista_paginador'),

    path('autoridad-facultad/detalle/<int:id>', views_curricular.autoridad_facultad_detalle, name='autoridad_facultad_detalle'),
    path('autoridad-facultad/eliminar/<int:id>', views_curricular.autoridad_facultad_eliminar, name='autoridad_facultad_eliminar'),
    path('autoridad-facultad/guardar', views_curricular.autoridad_facultad_guardar, name='autoridad_facultad_guardar'),

    path('autoridad-programa-estudio/detalle/<int:id>', views_curricular.autoridad_programa_estudio_detalle, name='autoridad_programa_estudio_detalle'),
    path('autoridad-programa-estudio/eliminar/<int:id>', views_curricular.autoridad_programa_estudio_eliminar, name='autoridad_programa_estudio_eliminar'),
    path('autoridad-programa-estudio/guardar', views_curricular.autoridad_programa_estudio_guardar, name='autoridad_programa_estudio_guardar'),

    path('facultad/detalle/<int:id>', views_curricular.facultad_detalle, name='facultad_detalle'),
    path('facultad/eliminar/<int:id>', views_curricular.facultad_eliminar, name='facultad_eliminar'),
    path('facultad/guardar', views_curricular.facultad_guardar, name='facultad_guardar'),
    path('facultad/lista', views_curricular.facultad_lista, name='facultad_lista'),

    path('nivel/detalle/<int:id>', views_curricular.nivel_detalle, name='nivel_detalle'),
    path('nivel/eliminar/<int:id>', views_curricular.nivel_eliminar, name='nivel_eliminar'),
    path('nivel/guardar', views_curricular.nivel_guardar, name='nivel_guardar'),

    path('pensum/detalle/<int:id>', views_curricular.pensum_detalle, name='pensum_detalle'),
    path('pensum/eliminar/<int:id>', views_curricular.pensum_eliminar, name='pensum_eliminar'),
    path('pensum/guardar', views_curricular.pensum_guardar, name='pensum_guardar'),
    path('pensum/guardar/pensums-grupo', views_curricular.pensum_guardar_pensums_grupo, name='pensum_guardar_pensums_grupo'),
    path('pensum/lista', views_curricular.pensum_lista, name='pensum_lista'),

    path('pensum-complementario/eliminar/<int:id>', views_curricular.pensum_complementario_eliminar, name='pensum_complementario_eliminar'),
    path('pensum-complementario/guardar', views_curricular.pensum_complementario_guardar, name='pensum_complementario_guardar'),

    path('pensum-grupo/detalle/<int:id>', views_curricular.pensum_grupo_detalle, name='pensum_grupo_detalle'),
    path('pensum-grupo/eliminar/<int:id>', views_curricular.pensum_grupo_eliminar, name='pensum_grupo_eliminar'),
    path('pensum-grupo/guardar', views_curricular.pensum_grupo_guardar, name='pensum_grupo_guardar'),
    path('pensum-grupo/lista', views_curricular.pensum_grupo_lista, name='pensum_grupo_lista'),

    path('programa-estudio/detalle/<int:id>', views_curricular.programa_estudio_detalle, name='programa_estudio_detalle'),
    path('programa-estudio/eliminar/<int:id>', views_curricular.programa_estudio_eliminar, name='programa_estudio_eliminar'),
    path('programa-estudio/guardar', views_curricular.programa_estudio_guardar, name='programa_estudio_guardar'),
    path('programa-estudio/lista', views_curricular.programa_estudio_lista, name='programa_estudio_lista'),
    path('programa-estudio/lista-paginador', views_curricular.programa_estudio_lista_paginador, name='programa_estudio_lista_paginador'),
    path('programa-estudio/lista-perfil', views_curricular.programa_estudio_lista_perfil, name='programa_estudio_lista_perfil'),
    path('programa-estudio/detalle-perfil/<int:id>', views_curricular.programa_estudio_detalle_perfil, name='programa_estudio_detalle_perfil'),

    path('titulo/detalle/<int:id>', views_curricular.titulo_detalle, name='titulo_detalle'),
    path('titulo/eliminar/<int:id>', views_curricular.titulo_eliminar, name='titulo_eliminar'),
    path('titulo/guardar', views_curricular.titulo_guardar, name='titulo_guardar'),

    path('tipo-formacion/<str:regimen>', views_curricular.tipo_formacion, name='tipo_formacion'),
]
