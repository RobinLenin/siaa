import {CatalogoItem} from "./catalogo-item.model";

export class Persona {
    id: number;
    numero_documento: string;
    primer_nombre: string;
    primer_apellido: string;
    segundo_nombre: string;
    segundo_apellido: string;
    fecha_nacimiento: Date|string;
    profesion: string;
    correo_electronico: string;
    correo_electronico_alternativo: string;
    numero_libreta_militar: string;

    anios_residencia: number;
    discapacidad: boolean;
    porcentaje_discapacidad: string;
    fecha_registro_conadis: string;
    numero_carnet_conadis: string;
    tipo_documento: CatalogoItem|any;

    sexo: CatalogoItem|any;
    estado_civil: CatalogoItem|any;
    tipo_etnia: CatalogoItem|any;
    tipo_sangre: CatalogoItem|any;
    condicion_cedulado: CatalogoItem|any;
    nacionalidad: CatalogoItem|any;
    nacionalidad_indigena: CatalogoItem|any;
    tipo_discapacidad: CatalogoItem|any;
    grado_discapacidad: CatalogoItem|any;

    edad: string;
    nombres_completos: string;
    foto_url: string
}

export interface PersonaResponse {
    status: number;
    data: Persona;
    message: string;
    count: number
}
