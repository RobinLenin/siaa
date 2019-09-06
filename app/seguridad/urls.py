# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from app.seguridad import views

admin.autodiscover()
app_name = 'seguridad'
urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^usuario/perfil$', views.usuario_perfil, name='usuario_perfil'),
    url(r'^usuario/actualizar-fotografia/(?P<id>[\d]+)$', views.usuario_actualizar_fotografia, name='usuario_actualizar_fotografia')
]
