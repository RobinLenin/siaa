export class CatalogoItem {
    id:number;
    nombre: string;
    descripcion: string;
    codigo_th: string;
    codigo_sg: string;
    activo: boolean;
    orden: number;
    padre:CatalogoItem;
}

export interface CatalogoItemsResponse {
    status: number;
    data: CatalogoItem[];
    message: string;
    count: number
}

export interface CatalogoItemResponse {
    status: number;
    data: CatalogoItem;
    message: string;
    count: number
}
