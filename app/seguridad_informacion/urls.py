from django.conf.urls import url

from app.seguridad_informacion import views
app_name = 'seguridad_informacion'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^cuenta-correo/consultar-numero-documento/(\d+)$', views.cuenta_correo_consultar_numero_documento),
    url(r'^cuenta-correo/detalle/(?P<id>[\d]+)$', views.cuenta_correo_detalle, name='cuenta_correo_detalle'),
    url(r'^cuenta-correo/guardar/$', views.cuenta_correo_guardar, name='cuenta_correo_guardar'),
    url(r'^cuenta-correo/lista$', views.cuenta_correo_lista, name='cuenta_correo_lista'),
    url(r'^cuenta-correo/lista-paginador', views.cuenta_correo_lista_paginador, name='cuenta_correo_lista_paginate'),
    url(r'^cuenta-correo/vincular/(?P<id>[\d]+)$', views.cuenta_correo_vincular, name='cuenta_correo_vincular'),
    url(r'^cuenta-correo/vincular-google$', views.cuenta_correo_vincular_google, name='cuenta_correo_vincular_google'),

    url(r'^grupo-ldap/crear$', views.grupo_ldap_crear, name='grupo_ldap_crear'),
    url(r'^grupo-ldap/detalle/(?P<id>[\d]+)$', views.grupo_ldap_detalle, name='grupo_ldap_detalle'),
    url(r'^grupo-ldap/lista$', views.grupo_ldap_lista, name='grupo_ldap_lista'),
    url(r'^grupo-ldap/usuario-agregar/(?P<id>[\d]+)/(?P<usuario_id>[\d]+)$', views.grupo_ldap_usuario_agregar, name='grupo_ldap_usuario_agregar'),
    url(r'^grupo-ldap/usuario-eliminar/(?P<id>[\d]+)/(?P<usuario_id>[\d]+)$', views.grupo_ldap_usuario_eliminar, name='grupo_ldap_usuario_eliminar'),
    url(r'^grupo-ldap/usuario-lista/(?P<id>[\d]+)$', views.grupo_ldap_usuario_lista, name='grupo_ldap_usuario_lista'),
    url(r'^grupo-ldap/vincular/(?P<id>[\d]+)$', views.grupo_ldap_vincular, name='grupo_ldap_vincular'),

    url(r'^usuario/actualizar-fotografia-all$', views.usuario_actualizar_fotografia_all, name='usuario_actualizar_fotografia_all'),
    url(r'^usuario/cambiar-estado/(?P<id>[\d]+)$', views.usuario_cambiar_estado, name='usuario_cambiar_estado'),
    url(r'^usuario/detalle/(?P<id>[\d]+)$', views.usuario_detalle, name='usuario_detalle'),
    url(r'^usuario/lista$', views.usuario_lista, name='usuario_lista'),
    url(r'^usuario/resetear-password/(?P<id>[\d]+)$', views.usuario_resetear_password, name='usuario_resetear_password'),
    url(r'^usuario/validar/(?P<id>[\d]+)$', views.usuario_validar, name='usuario_validar'),
    url(r'^usuario/vincular-google/(?P<id>[\d]+)$', views.usuario_vincular_google, name='usuario_vincular_google'),
    url(r'^usuario/vincular-ldap/(?P<id>[\d]+)$', views.usuario_vincular_ldap, name='usuario_vincular_ldap'),
    url(r'^usuario/vincular-ldap-all$', views.usuario_vincular_ldap_all, name='usuario_vincular_ldap_all'),

]
