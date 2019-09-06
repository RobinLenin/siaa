from django.conf.urls import url
from rest_framework.authtoken import views as views_token

from api.seguridad import views

urlpatterns = [
    url(r'^token/', views_token.obtain_auth_token),
    url(r'^usuario-logueado$', views.usuario_logueado),
    url(r'^usuario-logueado-funcionalidades$', views.usuario_logueado_funcionalidades)
]
