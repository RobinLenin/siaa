import {Persona} from '../../core/models/persona.model';
import {PuntoEmisionUAA} from './punto-emision-uaa.model';
import {OrdenPagoDetalle} from './orden-pago-detalle.model'
import {Direccion} from "../../core/models/direccion.model";
import {Pago} from "./pago.model";

export class OrdenPago {
    id: number;
    descripcion: string;
    estado: string;
    fecha_emision: string;
    fecha_vencimiento: string;
    referencia: string;
    referencia_externa: string;
    total: number;

    direccion: Direccion;
    ordenes_pago_detalle: OrdenPagoDetalle[];
    persona: Persona;
    punto_emision_uaa: PuntoEmisionUAA;
    pago: Pago;
}

export interface OrdenesPagoResponse {
    data: OrdenPago[];
    status: number;
    message: string;
}

export interface OrdenPagoResponse {
    data: OrdenPago;
    status: number;
    message: string;
}
