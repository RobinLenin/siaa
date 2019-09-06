import {CatalogoItem} from "../../core/models/catalogo-item.model";

export class Carrera {
    id: number;
    ies: number|any;
    codigo_senescyt: string;
    nombre: string;
    siglas: string;
    nivel_formacion: CatalogoItem|any;
    modalidad_estudios: CatalogoItem|any;
    fecha_creacion: Date;
    fecha_aprobacion: Date;
    numero_aprobacion: string;
    observacion: string;
    vigente: boolean;
}

export interface CarrerasResponse {
    status: number;
    data: Carrera[];
    message: string;
    count: number
}
