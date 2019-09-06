from django.conf.urls import url
from django.contrib import admin

from api.sga import views

admin.autodiscover()

urlpatterns = [
    url(r'^consultar-usuario-koha/(?P<cedula>[0-9]+)?$', views.consultar_usuario_koha),
]
