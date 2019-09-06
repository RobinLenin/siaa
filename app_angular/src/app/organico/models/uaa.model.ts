import {CatalogoItem} from "../../core/models/catalogo-item.model";
export class UAA {
    id: number;
    nombre: string;
    codigo: string;
    siglas: string;
    academico: boolean;
    administrativo: boolean;
    telefono: string;
    extension: string;
    correo: string;
    tipo_uaa: CatalogoItem;
    estructura_organica: CatalogoItem;
    estructura_organizacional: any;
    campus: any;
    localizacion: any;
    uaa: UAA | any;
    es_padre: boolean;
}

export interface IUaasResponse {
    status: number;
    data: UAA[];
    message: string;
    count: number
}
