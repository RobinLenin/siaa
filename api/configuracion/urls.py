from django.conf.urls import url

from api.configuracion import views

urlpatterns = [
    url(r'^detalle-parametrizacion-lista-por-padre$', views.detalle_parametrizacion_lista_por_padre),
    url(r'^detalle-parametrizacion-por-codigo$', views.detalle_parametrizacion_por_codigo),
]
