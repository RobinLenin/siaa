from django.conf.urls import url

from app.core.utils import validador
from . import views
app_name = 'core'
urlpatterns = [
    url(r'^direccion/crear/(?P<persona_id>[\d]+)$', views.direccion_crear, name='direccion_crear'),
    url(r'^direccion/editar/(?P<id>[\d]+)$', views.direccion_editar, name='direccion_editar'),
    url(r'^direccion/eliminar/(?P<id>[\d]+)$', views.direccion_eliminar, name='direccion_eliminar'),
    url(r'^direccion/guardar/(?P<persona_id>[\d]+)$', views.direccion_guardar, name='direccion_guardar'),

    url(r'^persona/editar/(?P<id>[\d]+)$', views.persona_editar, name='persona_editar'),
    url(r'^persona/guardar$', views.persona_guardar, name='persona_guardar'),

    url(r'^relacion/buscar/(?P<persona_id>[\d]+)$', views.relacion_buscar, name='relacion_buscar'),
    url(r'^relacion/crear/(?P<persona_id>[\d]+)$', views.relacion_crear, name='relacion_crear'),
    url(r'^relacion/editar/(?P<id>[\d]+)$', views.relacion_editar, name='relacion_editar'),
    url(r'^relacion/eliminar/(?P<id>[\d]+)$', views.relacion_eliminar, name='relacion_eliminar'),
    url(r'^relacion/guardar/(?P<persona_id>[\d]+)$', views.relacion_guardar, name='relacion_guardar'),

    url(r'^validar/campo-unico/', validador.validar_campo_unico, name='validar_campo_unico'),
]