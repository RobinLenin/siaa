from django.urls import path

from app.academico.views import views_periodo_academico

urlpatterns = [
    path('oferta-academica/detalle/<int:id>', views_periodo_academico.oferta_academica_detalle, name='oferta_academica_detalle'),
    path('oferta-academica/eliminar/<int:id>', views_periodo_academico.oferta_academica_eliminar, name='oferta_academica_eliminar'),
    path('oferta-academica/guardar', views_periodo_academico.oferta_academica_guardar, name='oferta_academica_guardar'),

    path('oferta-pensum/detalle/<int:id>', views_periodo_academico.oferta_pensum_detalle, name='oferta_pensum_detalle'),
    path('oferta-pensum/eliminar/<int:id>', views_periodo_academico.oferta_pensum_eliminar),
    path('oferta-pensum/guardar', views_periodo_academico.oferta_pensum_guardar),

    path('oferta-asignatura-nivel/eliminar/<int:id>', views_periodo_academico.oferta_asignatura_nivel_eliminar),
    path('oferta-asignatura-nivel/guardar', views_periodo_academico.oferta_asignatura_nivel_guardar),

    path('periodo-academico/detalle/<int:id>', views_periodo_academico.periodo_academico_detalle, name='periodo_academico_detalle'),
    path('periodo-academico/eliminar/<int:id>', views_periodo_academico.periodo_academico_eliminar, name='periodo_academico_eliminar'),
    path('periodo-academico/guardar', views_periodo_academico.periodo_academico_guardar, name='periodo_academico_guardar'),
    path('periodo-academico/lista', views_periodo_academico.periodo_academico_lista, name='periodo_academico_lista'),

    path('periodo-matricula/eliminar/<int:id>', views_periodo_academico.periodo_matricula_eliminar, name='periodo_matricula_eliminar'),
    path('periodo-matricula/guardar', views_periodo_academico.periodo_matricula_guardar, name='periodo_matricula_guardar')

]
