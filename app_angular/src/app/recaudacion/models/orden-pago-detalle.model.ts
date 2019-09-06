import { OrdenPago }  from './orden-pago.model';
import { Producto }   from './producto.model';
import { DetalleParametrizacion }   from '../../configuracion/models/detalle-parametrizacion.model';

export class OrdenPagoDetalle {
    id:number;
    secuencial:number;
    cantidad : number|any;
    precio : number|any;
    impuesto : number|any;
    impuesto_tarifa : number;
    impuesto_codigo :string;
    total: number|any;
    observacion: string="";
    producto: Producto|any;
    producto_codigo : string;
    producto_descripcion : string;
    orden_pago: OrdenPago|any;
    tipo_impuesto:DetalleParametrizacion|any;
    transferencia: boolean=false;
    estado: string;
}
