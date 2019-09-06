import {CatalogoItem} from "./catalogo-item.model";
import {Persona} from "../../core/models/persona.model";

export class Direccion {
    id: number;
    persona: Persona|number;
    tipo_direccion: CatalogoItem|number;
    numero: string;
    calle_principal: string;
    calle_secundaria: string;
    referencia: string;
    celular: string;
    telefono: string;
    extension: string;
}

export interface DireccionesResponse {
    status: number;
    data: Direccion[];
    message: string;
    count: number
}
