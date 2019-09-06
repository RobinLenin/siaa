import {Usuario} from "../../seguridad/models/usuario.model";

export class Funcionario {
    id: number;
    activo: boolean;
    usuario: Usuario | any;
    get_foto_url: string;
    get_nombres: string;
    get_apellidos: string;
}

export interface FuncionariosResponse {
    status: number;
    data: Funcionario[];
    message: string;
    count: number
}
