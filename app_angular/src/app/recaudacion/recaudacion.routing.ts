import {ModuleWithProviders} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';

import {ProductoListComponent} from './components/producto/producto-list.component';
import {ProductoDetailComponent} from './components/producto/producto-detail.component';
import {OrdenPagoListComponent} from './components/orden-pago/orden-pago-list.component';
import {OrdenPagoDetailComponent} from './components/orden-pago/orden-pago-detail.component';
import {OrdenPagoValidarListComponent} from "./components/orden-pago/orden-pago-validar-list.component";
import {OrdenPagoValidarDetailComponent} from "./components/orden-pago/orden-pago-validar-detail.component";
import {PuntoEmisionListComponent} from './components/punto-emision/punto-emision-list.component';
import {PuntoEmisionDetailComponent} from './components/punto-emision/punto-emision-detail.component';
import {FacturaEmisionListComponent} from './components/factura-emision/factura-emision-list.component';
import {ReportesRecaudacionUaaComponent} from './components/reportes/reportes-recaudacion-uaa.component';
import {ReportesRecaudacionAdminComponent} from "./components/reportes/reportes-recaudacion-admin.component";


export const recaudacionRoutes: Routes = [
    {path: 'recaudacion-producto-list', component: ProductoListComponent},
    {path: 'recaudacion-producto-detail/:id', component: ProductoDetailComponent},
    {path: 'recaudacion-orden-pago-list', component: OrdenPagoListComponent},
    {path: 'recaudacion-orden-pago-detail/:id', component: OrdenPagoDetailComponent},
    {path: 'recaudacion-orden-pago-validar-list', component: OrdenPagoValidarListComponent},
    {path: 'recaudacion-orden-pago-validar-detail/:id', component: OrdenPagoValidarDetailComponent},
    {path: 'recaudacion-punto-emision-list', component: PuntoEmisionListComponent},
    {path: 'recaudacion-punto-emision-detail/:id', component: PuntoEmisionDetailComponent},
    {path: 'recaudacion-factura-emision-list', component: FacturaEmisionListComponent},
    {path: 'recaudacion-reportes-uaa', component: ReportesRecaudacionUaaComponent},
    {path: 'recaudacion-reportes-admin', component: ReportesRecaudacionAdminComponent},
];

export const RecaudacionRouting: ModuleWithProviders = RouterModule.forChild(recaudacionRoutes);
