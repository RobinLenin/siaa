from django.conf.urls import url

from api.curricular import views

urlpatterns = [
    url(r'^carrera-lista-vigentes$', views.carrera_lista_vigentes),
]
