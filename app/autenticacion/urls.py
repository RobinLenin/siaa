from django.conf.urls import url
from app.autenticacion import views
app_name = 'autenticacion'
urlpatterns = [
    url(r'^cambiar-contrasena', views.cambiar_contrasena, name='cambiar_contrasena'),
    url(r'^cerrar-sesion', views.cerrar_sesion, name='cerrar_sesion'),
    url(r'^iniciar-sesion', views.iniciar_sesion, name='iniciar_sesion')
]
