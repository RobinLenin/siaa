import {CatalogoItem} from '../../core/models/catalogo-item.model';
import {DetalleParametrizacion} from '../../configuracion/models/detalle-parametrizacion.model';
export class Producto {
    id:number;
    codigo:string;
    descripcion:string;
    valor:number;
    facturable:boolean;
    activo:boolean;
    editable: boolean;
    tipo_factura:CatalogoItem|any;
    tipo_unidad:CatalogoItem|any;
    tipo_impuesto:DetalleParametrizacion|any;
    uaas:any[] = [];
}

export interface IProductoResponse{
    status: number;
    message: string;
    data: Producto;
}
export interface IProductosResponse{
    status: number;
    message: string;
    data: Producto[];
}
