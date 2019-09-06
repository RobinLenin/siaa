/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import { ModuleWithProviders } from '@angular/core';
import { Routes,RouterModule }        from '@angular/router';
import { PrestacionListComponent }    from './prestacion-list.component';
import { PrestacionAdminComponent }    from './prestacion-admin.component';

export const prestacionRoutes: Routes = [
  { path: 'prestaciones', component: PrestacionListComponent},
  { path: 'prestacion', component: PrestacionAdminComponent}

];

export const PrestacionRouting: ModuleWithProviders = RouterModule.forChild(prestacionRoutes);


