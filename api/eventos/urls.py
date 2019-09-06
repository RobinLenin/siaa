from django.urls import path

from api.eventos import views

urlpatterns = [
    path('consulta-persona/<str:numero_documento>', views.consultar_persona),
    path('orden-pago-estado/<int:id>', views.orden_pago_estado),
    path('orden-pago-guardar', views.orden_pago_guardar),
]
