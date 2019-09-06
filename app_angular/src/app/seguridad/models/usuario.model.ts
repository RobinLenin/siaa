import {Persona} from "../../core/models/persona.model";

export class Usuario {
    nombre_de_usuario: string;
    correo_electronico_institucional: string;
    foto_url: string;
    persona: Persona | any;
}