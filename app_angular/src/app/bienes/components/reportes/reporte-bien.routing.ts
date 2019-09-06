/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import { ModuleWithProviders } from '@angular/core';
import { Routes, RouterModule }        from '@angular/router';
import { RepPrestacionComponent }    from './rep-prestacion.component';


export const reportesBienRoutes: Routes = [
    { path: 'prestaciones-reporte', component: RepPrestacionComponent },

];

export const ReporteBienRouting: ModuleWithProviders = RouterModule.forChild(reportesBienRoutes);


