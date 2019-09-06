/* Autor: Yazber Romero.
 * Fecha: 05/10/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        05/10/2016                   	    Implementación inicial.
 */ 
import {IDetallePrestacion}from './IDetallePrestacion';

export interface IPrestacion {
    id: number;
    codigo: string;
    fecha_registro: string;
    tipo_id: number;
    usuario_id:number;
    detalles: IDetallePrestacion[];
}


export interface IPrestacionResponse {
    data: IPrestacion,
    status: number,
    mensaje: string,
    message: string,
}
