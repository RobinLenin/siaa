__author__ = 'dmunoz'
from django.conf.urls import url
from django.contrib import admin
from . import  views

admin.autodiscover()

urlpatterns = [
    url(r'^autenticar-usuario/(?P<user_name>[\w.@]+)/(?P<password>[\w\W]+)$', views.autenticar_usuario),
    url(r'^cambiar-password/(?P<user_name>[\w.@]+)/(?P<password>[\w\W]+)$', views.cambiar_password),
    url(r'^consultar-informacion/(?P<user_name>[\w.@]+)$', views.consultar_informacion),
]
