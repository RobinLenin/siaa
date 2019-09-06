from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from api.recaudacion import views

router = DefaultRouter(trailing_slash=False)
router.register(r'productos', views.ProductoViewSet, base_name='productos')
router.register(r'puntos-emision', views.PuntoEmisionViewSet, base_name='puntos-emision')
router.register(r'ordenes-pago', views.OrdenPagoViewSet, base_name='ordenes-pago')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^comprobante-reporte-detalle$', views.comprobante_reporte_detalle),
    url(r'^comprobante-reporte-generadas$', views.comprobante_reporte_generadas),
    url(r'^comprobante-reporte-guardadas$', views.comprobante_reporte_guardadas),
    url(r'^orden-pago-reporte-detalle$', views.orden_pago_reporte_detalle),
    url(r'^orden-pago-reporte-consolidado$', views.orden_pago_reporte_consolidado),
    url(r'^orden-pago-reporte-productos$', views.orden_pago_reporte_productos),
]
