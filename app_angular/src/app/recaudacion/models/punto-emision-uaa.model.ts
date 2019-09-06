import { PuntoEmision } from './punto-emison.model'
import {Funcionario} from "../../talento-humano/models/funcionario.model";

export class PuntoEmisionUAA {
    id:number;
    codigo:string;
    descripcion: string;
    punto_emision:PuntoEmision|number;
    funcionario: Funcionario|number;
    secuencial:number;
    impresora:string
}

interface AuxPuntoEmision{
    punto_emision: PuntoEmision;
    punto_emision_uaa: PuntoEmisionUAA[];
}

export interface PuntoEmisionUAAResponse{
    status: number;
    data: AuxPuntoEmision;
    message: string;
}

export interface PuntosEmisionUAAResponse{
    status: number;
    message: string;
    data: PuntoEmisionUAA[];
}

