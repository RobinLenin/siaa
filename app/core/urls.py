from django.conf.urls import url

from app.core.utils import validador
from . import views
app_name = 'core'
urlpatterns = [
    url(r'^direccion/crear/(?P<persona_id>[\d]+)$', views.direccion_crear, name='direccion_crear'),
    url(r'^direccion/editar/(?P<id>[\d]+)$', views.direccion_editar, name='direccion_editar'),
    url(r'^direccion/eliminar/(?P<id>[\d]+)$', views.direccion_eliminar, name='direccion_eliminar'),
    url(r'^direccion/guardar/(?P<persona_id>[\d]+)$', views.direccion_guardar, name='direccion_guardar'),
    #agregados
    url(r'^direccion/crear_momentaneo/(?P<persona_id>[\d]+)$', views.direccion_crear_momentaneo, name='direccion_crear_momentaneo'),
    url(r'^direccion/editar_momentaneo/(?P<id>[\d]+)$', views.direccion_editar_momentaneo, name='direccion_editar_momentaneo'),
    url(r'^direccion/guardar_momentaneo/(?P<persona_id>[\d]+)$', views.direccion_guardar_momentaneo, name='direccion_guardar_momentaneo'),
    url(r'^direccion/basico_guardar/(?P<persona_id>[\d]+)$', views.direccion_basico_guardar, name='direccion_basico_guardar'),
    url(r'^direccion/basico_detalle/(?P<id>[\d]+)$', views.direccion_basico_detalle, name='direccion_basico_detalle'),

    url(r'^persona/editar/(?P<id>[\d]+)$', views.persona_editar, name='persona_editar'),
    url(r'^persona/guardar$', views.persona_guardar, name='persona_guardar'),
    ##agregados

    url(r'^persona/crear_basico/(?P<cedula>[\d]+)', views.persona_basico_registro, name='persona_basico_registro'),
    url(r'^persona/editar_momentaneo/(?P<id>[\d]+)$', views.persona_editar_momentaneo, name='persona_editar_momentaneo'),
    url(r'^persona/guardar_nuevo$', views.persona_guardar_momentaneo, name='persona_guardar_momentaneo'),
    url(r'^persona/listar_momentaneo/', views.persona_listar_momentaneo, name='persona_listar_momentaneo'),
    url(r'^persona/guardar_momentaneo$', views.persona_guardar_momentaneo_adm, name='persona_guardar_momentaneo_adm'),
    url(r'^persona/basico_guardar$', views.persona_basico_guardar, name='persona_basico_guardar'),

    url(r'^relacion/buscar/(?P<persona_id>[\d]+)$', views.relacion_buscar, name='relacion_buscar'),
    url(r'^relacion/crear/(?P<persona_id>[\d]+)$', views.relacion_crear, name='relacion_crear'),
    url(r'^relacion/editar/(?P<id>[\d]+)$', views.relacion_editar, name='relacion_editar'),
    url(r'^relacion/eliminar/(?P<id>[\d]+)$', views.relacion_eliminar, name='relacion_eliminar'),
    url(r'^relacion/guardar/(?P<persona_id>[\d]+)$', views.relacion_guardar, name='relacion_guardar'),

    url(r'^validar/campo-unico/', validador.validar_campo_unico, name='validar_campo_unico'),
    url(r'^validar/numero-documento/', validador.validar_numero_documento, name='validar_numero_documento'),
]