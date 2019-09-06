export class PuntoEmision {
    id: number;
    activo: boolean;
    descripcion: string;
    codigo_establecimiento: string;
    codigo_facturero: string;
    nro_desde: number;
    nro_hasta: number;
}
export interface PuntoEmisionResponse{
    data: PuntoEmision;
    status: number;
    message: string;
}
export interface PuntosEmisionResponse{
    data: PuntoEmision[];
    status: number;
    message: string;
}

