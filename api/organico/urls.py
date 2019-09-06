from django.conf.urls import url

from api.organico import views

urlpatterns = [
    url(r'^uaa-lista-padres$', views.uaa_lista_padres),
    url(r'^uaa-lista-hijas$', views.uaa_lista_hijas),
]
