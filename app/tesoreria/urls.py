from django.urls import path

from app.tesoreria import views

app_name = 'tesoreria'
urlpatterns = [
    path('index', views.index_tesoreria, name='index_tesoreria'),

    path('cliente/informacion_detallada/<int:id>', views.cliente_informacion_detallada,
         name='cliente_informacion_detallada'),
    path('cliente/lista', views.cliente_lista, name='cliente_lista'),
    path('cliente/lista-paginador', views.cliente_lista_paginador, name='cliente_lista_paginador'),

    path('comentario/detalle/<int:id>', views.comentario_detalle, name='comentario_detalle'),
    path('comentario/eliminar/<int:id>', views.comentario_eliminar, name='comentario_eliminar'),
    path('comentario/guardar', views.comentario_guardar, name='comentario_guardar'),

    path('cuenta_cobrar/buscar', views.cuenta_cobrar_buscar, name='cuenta_cobrar_buscar'),
    path('cuenta_cobrar/detalle/<int:id>', views.cuenta_cobrar_detalle, name='cuenta_cobrar_detalle'),
    path('cuenta_cobrar/eliminar/<int:id>', views.cuenta_cobrar_eliminar, name='cuenta_cobrar_eliminar'),
    path('cuenta_cobrar/guardar', views.cuenta_cobrar_guardar, name='cuenta_cobrar_guardar'),
    path('cuenta_cobrar/listar', views.cuenta_cobrar_listar, name='cuenta_cobrar_listar'),
    path('cuenta_cobrar/lista-paginador', views.cuenta_cobrar_lista_paginador, name='cuenta_cobrar_lista_paginador'),


    path('cuenta_cobrar/abonos/eliminar/<int:id>', views.abono_eliminar, name='abono_eliminar'),
    path('cuenta_cobrar/abonos/guardar', views.abono_guardar, name='abono_guardar'),
    path('cuenta_cobrar/abonos/imprimir/<int:id>', views.abono_imprimir, name='abono_imprimir'),
    path('cuenta_cobrar/abonos/calcular', views.cuenta_cobrar_get_saldo, name='cuenta_cobrar_get_saldo'),



    path('interes_mensual/eliminar/<int:id>', views.interes_mensual_eliminar, name='interes_mensual_eliminar'),
    path('interes_mensual/guardar', views.interes_mensual_guardar, name='interes_mensual_guardar'),


    path('tasa_interes/detalle/<int:id>', views.tasa_interes_detalle, name='tasa_interes_detalle'),
    path('tasa_interes/eliminar/<int:id>', views.tasa_interes_eliminar, name='tasa_interes_eliminar'),
    path('tasa_interes/aplicar/<int:id>', views.tasa_interes_aplicar, name='tasa_interes_aplicar'),
    path('tasa_interes/guardar', views.tasa_interes_guardar, name='tasa_interes_guardar'),
    path('tasa_interes/listar', views.tasa_interes_listar, name='tasa_interes_listar'),
    path('tasa_interes/lista-paginador', views.tasa_interes_lista_paginador, name='tasa_interes_lista_paginador'),


]
