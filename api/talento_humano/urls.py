from django.conf.urls import url

from api.talento_humano import views

urlpatterns = [
    url(r'^funcionario-lista$', views.funcionario_lista),
]
