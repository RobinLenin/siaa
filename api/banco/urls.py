from django.urls import path

from api.banco import views

urlpatterns = [
    path('pago-abonar', views.pago_abonar),
    path('pago-lista/<str:identificacion>/<str:codigo_institucion>', views.pago_lista),
    path('pago-reverso/<str:secuencia_banco>/<int:secuencia_unl>', views.pago_reverso),
]
