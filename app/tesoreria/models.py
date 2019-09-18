from datetime import date, timezone

from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

# Create your models here.
#from rest_framework.fields import CharField
from django.db.models import Q

from app.core.models import Persona


class CuentaCobrar(models.Model):
    estado = models.BooleanField(default=True)
    concepto = models.CharField(max_length=100)
    fecha_emision = models.DateField(verbose_name="Fecha de emision")
    fecha_vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    saldo = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    cliente = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name='clientes')
    numero_titulo = models.CharField(max_length=10)
    titulo = models.FileField(upload_to='tesoreria/')


    class Meta:
        verbose_name = "Cuenta por Cobrar"
        verbose_name_plural = "Cuentas por Cobrar"

    def __str__(self):
        return "%s" % self.concepto

    @staticmethod
    def buscar(criterio):
        """
        Buscar registros por criterios
        :param criterio:
        :return:
        """
        if criterio:
            p_criterio = criterio.split(" ")
            qset = Q()
            for i in p_criterio:
                qset = qset & (Q(cliente__primer_apellido__icontains=i) | Q(
                    cliente__segundo_apellido__icontains=i) | Q(
                    cliente__primer_nombre__icontains=i) | Q(
                    cliente__segundo_nombre__icontains=i) | Q(
                    cliente__numero_documento__icontains=i))
        return CuentaCobrar.objects.filter(qset).distinct()

class Abono(models.Model):
    FORMA_PAGO_EFECTIVO = "Efectivo"
    FORMA_PAGO_CHEQUE = "Cheque"
    FORMA_PAGO_DEPOSITO = "Deposito"
    FORMAPAGO = ((FORMA_PAGO_EFECTIVO, "Efectivo"), (FORMA_PAGO_CHEQUE, "Cheque"), (FORMA_PAGO_DEPOSITO, "Deposito"),)

    forma_pago=models.CharField(max_length=10, choices=FORMAPAGO, default=FORMA_PAGO_EFECTIVO)
    referencia = models.CharField(max_length=100, default="")
    concepto = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    interes = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    fecha_pago= models.DateField()
    observacion= models.TextField()
    cuenta_cobrar = models.ForeignKey('CuentaCobrar', on_delete=models.CASCADE, related_name='abonos')

    def __str__(self):
        return "{0} {1} {2}".format(self.fecha_pago, self.monto, self.interes)

class Comentario(models.Model):
    cuenta_cobrar = models.ForeignKey('CuentaCobrar', on_delete=models.CASCADE, related_name='comentarios')
    fecha_creacion= models.DateTimeField(auto_now=True, verbose_name="Fecha de creacion")
    concepto = models.CharField(max_length=100)
    detalle= models.CharField(max_length=255)

    class Meta:
        verbose_name="Providencia"
        verbose_name_plural = "Providencias"
    def __str__(self):
        return "{0} {1}".format(self.fecha_creacion, self.concepto)

class TasaInteres(models.Model):
    tasa=models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    anio = models.DecimalField(max_digits=4, decimal_places=0, default=0)
    mes = models.DecimalField(max_digits=2, decimal_places=0, default=0)

    class Meta:
        verbose_name = "Tasa de Interes"
        verbose_name_plural = "Tasas de Interes"

    def __str__(self):
        return "{0} {1}".format(self.tasa, self.anio, self.mes)

class InteresMensual(models.Model):
    cuenta_cobrar = models.ForeignKey('CuentaCobrar', null=False, blank=False, on_delete=models.PROTECT, related_name='interesesmensuales')
    tasa = models.ForeignKey('TasaInteres', null=False, blank=False, on_delete=models.PROTECT, related_name='interesesmensuales')
    fecha = models.DateField()
    valor=models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    def __str__(self):
        return str(self.valor)

# todo corregir el models
# crear la url  -- metodo views -- html
# lista - crear - detalle - editar - eliminar
#