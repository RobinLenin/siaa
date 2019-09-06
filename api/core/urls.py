from django.conf.urls import url

from api.core import views

urlpatterns = [
    url(r'^catalogo-item-por-codigo$', views.catalogo_item_por_codigo),
    url(r'^catalogo-item-lista-por-catalogo$', views.catalogo_item_lista_por_catalogo),
    url(r'^canton-lista-por-provincia$', views.canton_lista_por_provincia),
    url(r'^pais-lista$', views.pais_lista),
    url(r'^provincia-lista-por-pais$', views.provincia_lista_por_pais),
    url(r'^parroquia-lista-por-canton$', views.parroquia_lista_por_canton),
    url(r'^parroquia-lista$', views.parroquia_lista),
    url(r'^persona-o-registrocivil$', views.persona_o_registrocivil),
    url(r'^persona-lista-paginacion$', views.persona_lista_paginacion),
    url(r'^persona-lista-direcciones$', views.persona_lista_direcciones),
]
