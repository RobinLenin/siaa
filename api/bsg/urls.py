__author__ = 'dmunoz'
from django.conf.urls import url
from django.contrib import admin
from api.bsg import views

admin.autodiscover()

urlpatterns = [
    url(r'^consultar-cedula/(?P<cedula>[\w|\W]+)?$', views.consultar_registrocivil_por_cedula),
    url(r'^consultar-nombres?$', views.consultar_registrocivil_por_nombres),
    url(r'^consultar-discapacidad/(?P<cedula>[\w|\W]+)?$', views.consultar_discapacidad_por_cedula),
    url(r'^consultar-titulos/(?P<cedula>[\w|\W]+)?$', views.consultar_titulos_por_cedula),

    url(r'^consultar-cedula-varios?$', views.consultar_registrocivil_all_cedulas),
    url(r'^consultar-discapacidad-varios?$', views.consultar_discapacidades_all_cedulas),
    url(r'^consultar-titulos-varios?$', views.consultar_titulos_all_cedulas),
]

