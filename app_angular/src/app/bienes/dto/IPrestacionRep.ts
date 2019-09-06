/* Autor: Yazber Romero.
 * Fecha: 05/10/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        05/10/2016                   	    Implementación inicial.
 */
import {IPersona} from './IPersona'

export interface IPrestacionRep {
    mes: string;
    idMes: number;
    carreraId: string;
    carreraNombre: string;
    cantidad: number;
    anio: number;
    persona:IPersona[];
}


export interface IPrestacionRepsResponse {
    status: number;
    data: IPrestacionRep[];
    message: string;
    count: number
}

