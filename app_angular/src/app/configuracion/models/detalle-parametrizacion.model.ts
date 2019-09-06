export class DetalleParametrizacion {
    id:number;
    codigo : string;
    nombre : string;
    valor : string;
}

export interface DetalleParametrizacionResponse {
    status: number;
    data: DetalleParametrizacion;
    message: string;
    count: number
}