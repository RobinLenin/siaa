from django.conf.urls import url

from .views import views_pedi
from .views import views_poa

__author__ = 'jose.martinez'
app_name = 'planificacion'
urlpatterns = [
    url(r'^$', views_pedi.index, name='index'),

    url(r'^estrategia/guardar$', views_pedi.estrategia_guardar, name='estrategia_guardar'),
    url(r'^estrategia/eliminar/(?P<id>[\d]+)$', views_pedi.estrategia_eliminar, name='estrategia_eliminar'),

    url(r'^indicador/guardar/$', views_pedi.indicador_guardar, name='indicador_guardar'),
    url(r'^indicador/detalle/(?P<id>[\d]+)$', views_pedi.indicador_detalle, name='indicador_detalle'),
    url(r'^indicador/eliminar/(?P<id>[\d]+)$', views_pedi.indicador_eliminar, name='indicador_eliminar'),

    url(r'^meta-anual/detalle/(?P<id>[\d]+)$', views_pedi.meta_anual_detalle, name='meta_anual_detalle'),
    url(r'^meta-anual/eliminar/(?P<id>[\d]+)$', views_pedi.meta_anual_eliminar),
    url(r'^meta-anual/guardar/$', views_pedi.meta_anual_guardar, name='meta_anual_guardar'),

    url(r'^objetivo-estrategico/detalle/(?P<id>[\d]+)$', views_pedi.objetivo_estrategico_detalle, name='objetivo_estrategico_detalle'),
    url(r'^objetivo-estrategico/guardar/$', views_pedi.objetivo_estrategico_guardar, name='objetivo_estrategico_guardar'),
    url(r'^objetivo-estrategico/eliminar/(?P<id>[\d]+)$', views_pedi.objetivo_estrategico_eliminar, name='objetivo_estrategico_eliminar'),

    url(r'^objetivo-operativo/detalle/(?P<id>[\d]+)$', views_pedi.objetivo_operativo_detalle, name='objetivo_operativo_detalle'),
    url(r'^objetivo-operativo/guardar$', views_pedi.objetivo_operativo_guardar, name='objetivo_operativo_guardar'),
    url(r'^objetivo-operativo/eliminar/(?P<id>[\d]+)$', views_pedi.objetivo_operativo_eliminar, name='objetivo_operativo_eliminar'),

    url(r'^plan-estrategico/lista$', views_pedi.plan_estrategico_lista, name='plan_estrategico_lista'),
    url(r'^plan-estrategico/detalle/(?P<id>[\d]+)$', views_pedi.plan_estrategico_detalle, name='plan_estrategico_detalle'),
    url(r'^plan-estrategico/guardar$', views_pedi.plan_estrategico_guardar, name='plan_estrategico_guardar'),
    url(r'^plan-estrategico/eliminar/(?P<id>[\d]+)$', views_pedi.plan_estrategico_eliminar, name='plan_estrategico_eliminar'),
    url(r'^plan-estrategico/reporte-detalle/(?P<id>[\d]+)$', views_pedi.plan_estrategico_reporte_detalle, name='plan_estrategico_reporte_detalle'),

    url(r'^politica/guardar$', views_pedi.politica_guardar, name='politica_guardar'),
    url(r'^politica/eliminar/(?P<id>[\d]+)$', views_pedi.politica_eliminar, name='politica_eliminar'),

    url(r'^resultado/detalle/(?P<id>[\d]+)$', views_pedi.resultado_detalle, name='resultado_detalle'),
    url(r'^resultado/guardar/$', views_pedi.resultado_guardar, name='resultado_guardar'),
    url(r'^resultado/eliminar/(?P<id>[\d]+)$', views_pedi.resultado_eliminar, name='resultado_eliminar'),



    # POA
    url(r'^actividad/guardar$', views_poa.actividad_guardar, name='actividad_guardar'),
    url(r'^actividad/detalle/(?P<id>[\d]+)$', views_poa.actividad_detalle, name='actividad_detalle'),
    url(r'^actividad/eliminar/(?P<id>[\d]+)$', views_poa.actividad_eliminar, name='actividad_eliminar'),

    url(r'^plan-operativo/lista$', views_poa.plan_operativo_lista, name='plan_operativo_lista'),
    url(r'^plan-operativo/guardar$', views_poa.plan_operativo_guardar, name='plan_operativo_guardar'),
    url(r'^plan-operativo/detalle/(?P<id>[\d]+)$', views_poa.plan_operativo_detalle, name='plan_operativo_detalle'),
    url(r'^plan-operativo/eliminar/(?P<id>[\d]+)$', views_poa.plan_operativo_eliminar, name='plan_operativo_eliminar'),

    url(r'^presupuesto/guardar$', views_poa.presupuesto_guardar, name='presupuesto_guardar'),
    url(r'^presupuesto/eliminar/(?P<id>[\d]+)$', views_poa.presupuesto_eliminar, name='presupuesto_eliminar'),

    url(r'^verificacion/guardar$', views_poa.verificacion_guardar, name='verificacion_guardar'),
    url(r'^verificacion/detalle/(?P<id>[\d]+)$', views_poa.verificacion_detalle, name='verificacion_detalle'),
    url(r'^verificacion/eliminar/(?P<id>[\d]+)$', views_poa.verificacion_eliminar, name='verificacion_eliminar'),

]



