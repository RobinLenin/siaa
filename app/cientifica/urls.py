from django.conf.urls import url
from . import views
app_name = 'cientifica'
urlpatterns = [

    url(r'^articulo-revista/crear/(?P<produccion_cientifica_id>[\d]+)$', views.articulo_revista_crear, name='articulo_revista_crear'),
    url(r'^articulo-revista/editar/(?P<id>[\d]+)$', views.articulo_revista_editar, name='articulo_revista_editar'),
    url(r'^articulo-revista/eliminar/(?P<id>[\d]+)$', views.articulo_revista_eliminar, name='articulo_revista_eliminar'),
    url(r'^articulo-revista/guardar/(?P<produccion_cientifica_id>[\d]+)$', views.articulo_revista_guardar, name='articulo_revista_guardar'),

    url(r'^capitulo-libro/crear/(?P<produccion_cientifica_id>[\d]+)$', views.capitulo_libro_crear, name='capitulo_libro_crear'),
    url(r'^capitulo-libro/editar/(?P<id>[\d]+)$', views.capitulo_libro_editar, name='capitulo_libro_editar'),
    url(r'^capitulo-libro/eliminar/(?P<id>[\d]+)$', views.capitulo_libro_eliminar, name='capitulo_libro_eliminar'),
    url(r'^capitulo-libro/guardar/(?P<produccion_cientifica_id>[\d]+)$', views.capitulo_libro_guardar, name='capitulo_libro_guardar'),

    url(r'^libro/crear/(?P<produccion_cientifica_id>[\d]+)$', views.libro_crear, name='libro_crear'),
    url(r'^libro/editar/(?P<id>[\d]+)$', views.libro_editar, name='libro_editar'),
    url(r'^libro/eliminar/(?P<id>[\d]+)$', views.libro_eliminar, name='libro_eliminar'),
    url(r'^libro/guardar/(?P<produccion_cientifica_id>[\d]+)$', views.libro_guardar, name='libro_guardar'),

    url(r'^ponencia/crear/(?P<produccion_cientifica_id>[\d]+)$', views.ponencia_crear, name='ponencia_crear'),
    url(r'^ponencia/editar/(?P<id>[\d]+)$', views.ponencia_editar, name='ponencia_editar'),
    url(r'^ponencia/eliminar/(?P<id>[\d]+)$', views.ponencia_eliminar, name='ponencia_eliminar'),
    url(r'^ponencia/guardar/(?P<produccion_cientifica_id>[\d]+)$', views.ponencia_guardar, name='ponencia_guardar'),

    url(r'^produccion-cientifica/crear/(?P<persona_id>[\d]+)$', views.produccion_cientifica_crear, name='produccion_cientifica_crear'),

]