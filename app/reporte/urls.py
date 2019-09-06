from django.conf.urls import url

from . import views
app_name = 'reporte'
urlpatterns = [
    url(r'^$', views.plantilla_lista),
    url(r'^plantilla/detalle/(?P<plantilla_id>[\d]+)$', views.plantilla_detalle, name='plantilla_detalle'),
    url(r'^plantilla/exportar/(?P<plantilla_id>[\d]+)$', views.plantilla_exportar, name='plantilla_exportar'),
    url(r'^plantilla/eliminar/(?P<plantilla_id>[\d]+)$', views.plantilla_eliminar),
    url(r'^plantilla/guardar-datos$', views.plantilla_guardar_datos),
    url(r'^plantilla/guardar-definicion$', views.plantilla_guardar_definicion),
    url(r'^plantilla/importar$', views.plantilla_importar, name='plantilla_importar'),
    url(r'^plantilla/lista/$', views.plantilla_lista, name='plantilla_lista'),
    url(r'^plantilla/vista-previa', views.plantilla_vista_previa, name='plantilla_vista_previa'),
]

