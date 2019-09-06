from django.db import models

from app.recaudacion.models import Producto


class Comprobante(models.Model):
    """
    Modelo que almacena datos del documento a emitir: Facturas, Notas de venta, Liquidaciones de compra de bienes
    y prestación de servicios, Comprobantes de Retención, Notas de crédito, Notas de debito ....
    """
    ESTADO_EMITIDA = 'EMITIDA'
    ESTADO_ANULADO = 'ANULADO'
    CHOICE_ESTADO = ((ESTADO_EMITIDA,'Emitida'),
                     (ESTADO_ANULADO,'Anulada'))

    persona = models.ForeignKey('core.Persona', on_delete=models.PROTECT)
    direccion = models.ForeignKey('core.Direccion', on_delete=models.PROTECT)
    fecha_emision = models.DateTimeField()
    numero_documento = models.TextField(unique=True)
    observacion = models.TextField(null=True, blank=True)
    tipo_documento = models.ForeignKey('core.CatalogoItem',
                                       limit_choices_to={'catalogo__codigo': 'TIPO_DOCUMENTO_CONTABLE'},
                                        on_delete = models.PROTECT)
    subtotal_descuento = models.DecimalField(max_digits=12, decimal_places=4)
    subtotal_sin_impuesto = models.DecimalField(max_digits=12, decimal_places=4)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=CHOICE_ESTADO, default=ESTADO_EMITIDA)

    orden_pago = models.OneToOneField('recaudacion.OrdenPago', on_delete=models.PROTECT, null=True)

class ComprobanteDetalle(models.Model):
    """
    Modelo que almacena el detalle de un  documento: Para implementar mayor funcionalidad
    se puede agregar un campo que haga relación al articulo
    """
    comprobante = models.ForeignKey(Comprobante, related_name='comprobante_detalles', on_delete=models.CASCADE)
    codigo = models.TextField()
    detalle = models.TextField()
    detalle_adicional = models.TextField(null=True, blank=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    precio = models.DecimalField(max_digits=12, decimal_places=4)
    descuento = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=4)
    impuesto = models.DecimalField(max_digits=12, decimal_places=4)
    tarifa_impuesto = models.DecimalField(max_digits=12, decimal_places=2)
    codigo_impuesto = models.TextField()
    tipo_impuesto = models.ForeignKey('configuracion.DetalleParametrizacion',
                                      limit_choices_to={'parametrizacion__codigo': 'TIPO_IMPUESTO'},
                                      on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

class ComprobanteImpuesto(models.Model):
    """
    Modelo que almacena la lista de impuestos de un  documento
    """
    comprobante = models.ForeignKey(Comprobante, related_name='comprobante_impuestos', on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=4)
    impuesto = models.DecimalField(max_digits=12, decimal_places=4)
    tarifa_impuesto = models.DecimalField(max_digits=12, decimal_places=2)
    codigo_impuesto = models.TextField()
    tipo_impuesto = models.ForeignKey('configuracion.DetalleParametrizacion',
                                      limit_choices_to={'parametrizacion__codigo': 'TIPO_IMPUESTO'},
                                      on_delete=models.PROTECT)

