/* Autor: Yazber Romero.
 * Fecha: 05/10/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        05/10/2016                   	    Implementación inicial.
 */
import {IPersona}from './IPersona';

export interface IDetallePrestacion {
    id: number;
    fecha_registro: string;
    fecha_finalizacion:string;
    hora_entrada: string;
    hora_salida: string;
    numero: number;
    persona: IPersona;
    persona_id: number;
    carrera_id: number;
    razon_id: number;
    estado_id: number;
    funcion_id: number;
    tipo_ente_id:number;   
    activo:boolean; 
    
}
