# Proyecto:siaa
# Autor   : Yazber Romero
# Fecha   :08/06/16 15:21

from django.conf.urls import url

from api.bienes import views
app_name = 'api_bienes'
urlpatterns = [
    url(r'^detalle-prestacion-guardar/(?P<id>[0-9]+)$', views.detalle_prestacion_guardar),
    url(r'^detalle-prestacion-lista$', views.detalle_prestacion_lista),
    url(r'^detalle-prestacion-filtro/(?P<fechaDesde>[\w|\W]+)/(?P<fechaHasta>[\w|\W]+)$', views.detalle_prestacion_filtro),
    url(r'^prestacion-guardar/(?P<token>[\w|\W]+)$', views.prestacion_guardar),
]
