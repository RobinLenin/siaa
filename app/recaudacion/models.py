# -*- encoding: utf-8 -*-
from django.db import models
from django.db.models.query_utils import Q

from app.organico.models import UAA
from app.talento_humano.models import Funcionario


class Pago(models.Model):

    FORMA_PAGO_DEPOSITO = 'DEPOSITO'
    FORMA_PAGO_DEPOSITO_CODIGO = 'DEPOSITO_CODIGO'
    FORMA_PAGO_EFECTIVO = 'EFECTIVO'
    FORMA_PAGO_TRANSFERENCIA = 'TRANSFERENCIA'
    FORMA_PAGO_TARJETA_CREDITO = 'TARJETA_CREDITO'
    CHOICE_FORMA_PAGO = ((FORMA_PAGO_DEPOSITO, "Depósito"),
                         (FORMA_PAGO_DEPOSITO_CODIGO, "Depósito por código de la solicitud"),
                         (FORMA_PAGO_EFECTIVO, "Efectivo"),
                         (FORMA_PAGO_TRANSFERENCIA, "Transferencia"),
                         (FORMA_PAGO_TARJETA_CREDITO, "Tarjeta de crédito"))


    forma_pago = models.CharField(choices=CHOICE_FORMA_PAGO, max_length=25, default=FORMA_PAGO_EFECTIVO)
    referencia = models.CharField(max_length=50, null=True, blank=True, unique=True)  # Generada por el banco si es deposito, transferencia
    depositante = models.TextField(null=True, blank=True)  # Si es deposito o tranferencia, nombre del depositante
    fecha_pago = models.DateTimeField()
    fecha_reverso = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class Producto(models.Model):
    codigo = models.TextField(unique=True)
    descripcion = models.TextField()
    valor = models.DecimalField(max_digits=12, decimal_places=4)
    activo = models.BooleanField(default=False, blank=True)
    facturable = models.BooleanField(default=False, blank=True)
    editable = models.BooleanField(default=False, blank=True)
    tipo_factura = models.ForeignKey('core.CatalogoItem', blank=True, null=True,
                                     related_name='tipo_factura',
                                     limit_choices_to={'catalogo__codigo': 'TIPO_FACTURA'},
                                     on_delete=models.SET_NULL)
    tipo_unidad = models.ForeignKey('core.CatalogoItem',
                                    related_name='tipo_unidad',
                                    limit_choices_to={'catalogo__codigo': 'TIPO_UNIDAD'},
                                    on_delete=models.PROTECT)
    tipo_impuesto = models.ForeignKey('configuracion.DetalleParametrizacion',
                                      related_name='tipo_iva',
                                      limit_choices_to={'parametrizacion__codigo': 'TIPO_IMPUESTO'},
                                      on_delete=models.PROTECT)

    uaas = models.ManyToManyField(UAA, related_name="uaas", blank=True)

    class Meta:
        ordering = ['codigo']

    @staticmethod
    def buscar(criterio):
        """
        Buscar registros por criterios
        :param criterio:
        :return:
        """
        qset = Q()
        if criterio:
            p_criterio = criterio.split(" ")
            for i in p_criterio:
                qset = qset & (
                        Q(codigo__icontains=i) | Q(descripcion__icontains=i) | Q(valor__icontains=i))
        return Producto.objects.filter(qset).distinct()


class PuntoEmision(models.Model):
    codigo_establecimiento = models.TextField()
    codigo_facturero = models.TextField()
    activo = models.BooleanField(default=False, blank=True)
    descripcion = models.TextField()
    nro_desde = models.CharField(max_length=10)  # secuencia inicial de la factura
    nro_hasta = models.CharField(max_length=10)  # secuencia final de la factura
    nro_secuencial = models.IntegerField(default=0)  # secuencial para la generación de nueva factura

    class Meta:
        ordering = ['codigo_establecimiento', 'codigo_facturero']

    def actualizar_secuencial(self):
        """
        Actualiza el secuencial para el control de las facturas
        :return:
        """
        self.nro_secuencial = self.nro_secuencial + 1
        self.save()

    def new_codigo_factura(self, secuencial):
        """
        Retorna un nuevo secuencial para una nueva factura
        :param secuencial:
        :return:
        """
        codigo_secuencial = "%09d" % secuencial
        codigo = "%s-%s-%s" % (self.codigo_establecimiento, self.codigo_facturero, codigo_secuencial)
        return codigo


class PuntoEmisionUAA(models.Model):
    codigo = models.TextField()
    descripcion = models.TextField()
    punto_emision = models.ForeignKey(PuntoEmision, on_delete=models.PROTECT)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT)
    secuencial = models.IntegerField(default=0)  # secuencial por uaa para una nueva orden de pago detalle
    impresora = models.CharField(max_length=10,
                                 default='default',
                                 choices=(('default', 'Impresora por defecto'),
                                          ('printers', 'Mostrar lista de Impresoras')))

    class Meta:
        ordering = ['codigo']

    def actualizar_secuencial(self):
        """
        Actualiza el secuencial para el control de las ordenes de pago detalle
        :return:
        """
        self.secuencial = self.secuencial + 1
        self.save()

    def new_secuencial_orden_pago_detalle(self):
        """
        Retorna un nuevo secuencial para una orden de pago detalle
        :return:
        """
        return self.secuencial


class OrdenPago(models.Model):
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_EMITIDA = 'EMITIDA'
    ESTADO_ANULADA = 'ANULADA'
    CHOICE_ESTADO = ((ESTADO_PENDIENTE, "Pendiente"),
                     (ESTADO_EMITIDA, "Emitida"),
                     (ESTADO_ANULADA, "Anulada"))

    fecha_emision = models.DateTimeField()
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    persona = models.ForeignKey('core.Persona', on_delete=models.PROTECT)
    direccion = models.ForeignKey('core.Direccion', on_delete=models.PROTECT, related_name='ordenes_pago_direccion')
    punto_emision_uaa = models.ForeignKey(PuntoEmisionUAA, on_delete=models.PROTECT, related_name='ordenes_pago', null=True)
    estado_orden = models.ForeignKey('core.CatalogoItem',
                                     related_name='estado_orden_pago',
                                     limit_choices_to={'catalogo__codigo': 'ESTADO_ORDEN_PAGO'},
                                     on_delete=models.PROTECT, null=True) #por borrar

    estado = models.CharField(choices=CHOICE_ESTADO, max_length=25, default=ESTADO_PENDIENTE)
    descripcion = models.TextField(null=True, blank=True)
    referencia = models.TextField(null=True, blank=True)
    referencia_externa = models.TextField(null=True,blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    pago = models.OneToOneField(Pago,on_delete=models.PROTECT, null=True)

    @staticmethod
    def buscar_por_punto_emision_uaa(criterio, punto_emison_uaa=None):
        """
        Buscar registros por criterios y por un punto de emsiisón uaa
        :param criterio:
        :param punto_emison_uaa:
        :return:
        """
        qset = Q()
        qset = qset & (Q(punto_emision_uaa=punto_emison_uaa))
        if criterio:
            p_criterio = criterio.split(" ")
            for i in p_criterio:
                qset = qset & (
                        Q(fecha_emision__icontains=i) |
                        Q(punto_emision_uaa__codigo__icontains=i) |
                        Q(estado__icontains=i) |
                        Q(persona__numero_documento__icontains=i) |
                        Q(persona__primer_nombre__icontains=i) |
                        Q(persona__segundo_nombre__icontains=i) |
                        Q(persona__primer_apellido__icontains=i) |
                        Q(persona__segundo_apellido__icontains=i) |
                        Q(descripcion__icontains=i)
                )
        return OrdenPago.objects.filter(qset).distinct().order_by('-fecha_emision', '-id')


class OrdenPagoDetalle(models.Model):
    secuencial = models.IntegerField(null=True)
    orden_pago = models.ForeignKey(OrdenPago, related_name='ordenes_pago_detalle', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    producto_codigo = models.TextField()
    producto_descripcion = models.TextField()
    cantidad = models.DecimalField(max_digits=12, decimal_places=4)
    precio = models.DecimalField(max_digits=12, decimal_places=4)
    impuesto = models.DecimalField(max_digits=12, decimal_places=4)
    impuesto_tarifa = models.DecimalField(max_digits=12, decimal_places=2)
    impuesto_codigo = models.TextField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)
    transferencia = models.BooleanField(default=False)
    tipo_impuesto = models.ForeignKey('configuracion.DetalleParametrizacion',
                                      limit_choices_to={'parametrizacion__codigo': 'TIPO_IMPUESTO'}, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=OrdenPago.CHOICE_ESTADO, default=OrdenPago.ESTADO_PENDIENTE)

    def get_codigo_punto_emision_uaa(self):
        """
        Retorna un string informativo del punto de emisión uaa con el secuencial
        :return:
        """
        return "%s-%s" % (self.orden_pago.punto_emision_uaa.codigo, self.secuencial)

    def get_formato_secuencial(self):
        """
        Retorna en formato de ceros a la izquierda del secuencial
        para ser mostrado
        :return:
        """
        return "%012d" % self.secuencial


class OrdenPagoDocumentoDetalle(models.Model):
    orden_pago_detalle = models.ForeignKey(OrdenPagoDetalle, on_delete=models.PROTECT,
                                           related_name='ords_pago_docs_detalle')
    comprobante_detalle = models.ForeignKey('tributacion.ComprobanteDetalle', on_delete=models.PROTECT)








