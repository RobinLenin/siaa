from django.urls import include
from django.urls import path

app_name = 'academico'

urlpatterns = [
    path('', include('app.academico.urls.curricular')),
    path('', include('app.academico.urls.periodo_academico')),
]
