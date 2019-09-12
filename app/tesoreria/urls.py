from django.urls import path

from app.tesoreria import views
app_name = 'tesoreria'
urlpatterns = [
    path('index', views.index_tesoreria, name='index_tesoreria'),

    path('cuenta_cobrar/listar', views.cuenta_cobrar_listar, name='cuenta_cobrar_listar'),
    path('cuenta_cobrar/lista-paginador', views.cuenta_cobrar_lista_paginador, name='cuenta_cobrar_lista_paginador'),
    path('cuenta_cobrar/buscar', views.cuenta_cobrar_buscar, name='cuenta_cobrar_buscar'),
    path('cuenta_cobrar/guardar', views.cuenta_cobrar_guardar, name='cuenta_cobrar_guardar'),
    path('cuenta_cobrar/eliminar/<int:id>', views.cuenta_cobrar_eliminar, name='cuenta_cobrar_eliminar'),
    path('cuenta_cobrar/detalle/<int:id>', views.cuenta_cobrar_detalle, name='cuenta_cobrar_detalle'),

    # path('cuenta_cobrar/titulo_credito/guardar', views.titulo_credito_guardar, name='titulo_credito.guardar'),
    # path('cuenta_cobrar/titulo_credito/eliminar', views.titulo_credito_eliminar, name='titulo_credito.eliminar'),

    path('comentario/guardar', views.comentario_guardar, name='comentario_guardar'),
    path('comentario/eliminar/<int:id>', views.comentario_eliminar, name='comentario_eliminar'),
    path('comentario/detalle/<int:id>', views.comentario_detalle, name='comentario_detalle'),
    # path('comentario/listar', views.comentario_listar, name='comentario.listar'),

    path('cuenta_cobrar/abonos/guardar', views.abono_guardar, name='abono_guardar'),
    path('cuenta_cobrar/abonos/eliminar/<int:id>', views.abono_eliminar, name='abono_eliminar'),
    path('cuenta_cobrar/abonos/imprimir/<int:id>', views.abono_imprimir, name='abono_imprimir'),


    path('tasa_interes/guardar', views.tasa_interes_guardar, name='tasa_interes_guardar'),
    path('tasa_interes/eliminar/<int:id>', views.tasa_interes_eliminar, name='tasa_interes_eliminar'),
    path('tasa_interes/listar', views.tasa_interes_listar, name='tasa_interes_listar'),
    path('tasa_interes/lista-paginador', views.tasa_interes_lista_paginador, name='tasa_interes_lista_paginador'),
    path('tasa_interes/buscar', views.tasa_interes_buscar, name='tasa_interes.buscar'),

    path('interes_mensual/guardar', views.interes_mensual_guardar, name='interes_mensual_guardar'),
    path('interes_mensual/eliminar/<int:id>', views.interes_mensual_eliminar, name='interes_mensual_eliminar'),
   # path('interes_mensual/listar', views.interes_mensual_listar, name='interes_mensual.listar'),

]
