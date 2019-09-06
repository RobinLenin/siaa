import {ICatalogoItem} from './ICatalogoItem'
export interface IPersona {
    id: number;
    tipo_documento: string;
    numero_documento: string;
    primer_apellido: string;
    segundo_apellido: string;
    primer_nombre: string;
    segundo_nombre: string;
    fecha_nacimiento: string;
    edad: number;
    sexo: ICatalogoItem[];
}

