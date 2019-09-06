__author__ = 'JJM'
from django.conf.urls import url
from django.contrib import admin
from . import  views

admin.autodiscover()

urlpatterns = [
    url(r'^validar-correo/(?P<correo>[\w|\W]+)?$', views.validar_correo),
]
