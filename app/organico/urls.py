from django.conf.urls import url
from . import views
app_name = 'organico'
urlpatterns = [
    url(r'^$', views.uaa_estructura, name='uaa_estructura'),
    url(r'^uaa/crear/(?P<padre_id>[\d]+)$', views.uaa_crear, name='uaa_crear'),
    url(r'^uaa/detalle/(?P<id>[\d]+)$', views.uaa_detalle, name='uaa_detalle'),
    url(r'^uaa/editar/(?P<id>[\d]+)$', views.uaa_editar, name='uaa_editar'),
    url(r'^uaa/eliminar/(?P<id>[\d]+)$', views.uaa_eliminar, name='uaa_eliminar'),
    url(r'^uaa/guardar$', views.uaa_guardar, name='uaa_guardar'),
]
