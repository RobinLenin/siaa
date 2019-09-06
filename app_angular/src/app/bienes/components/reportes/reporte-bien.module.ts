/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {CommonModule} from "@angular/common";
import {BaseToolBarModule} from "../toolbar/base-toolbar.module";
import {FechaMinMaxModule} from "../../../shared/comun/components/calendario/fecha-min-max.module";

import {MatIconModule, MatIconRegistry,
        MatButtonModule,
        MatCardModule,
        MatCheckboxModule,
        MatGridListModule,
        MatInputModule,
        MatListModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatRadioModule,
        MatSidenavModule,
        MatSlideToggleModule,
        MatSelectModule,
        MatTabsModule,
        MatToolbarModule,
        MatTableModule
    } from "@angular/material";


import {PaginadorNavegacionModule} from "../../../shared/comun/components/paginador-navegacion/paginador-navegacion.module";
import {SelectCarreraModule} from "../select-carrera/select-carrera.module";
import {SelectCatalogoItemModule} from "../../../shared/core/components/select-catalogo-item/select-item.module";
import {reporteDinamicoPipe} from "../../pipe/reporte-dinamico.pipe";

import {ConfigService} from "../../services/configure.service";
import {DetallePrestacionService} from "./../../services/detalle-prestacion.service";
import {ResourceService} from "./../../../shared/comun/services/resource.service";
import {UtilService} from "../../../shared/comun/services/util.service";

import {RepPrestacionComponent} from "./rep-prestacion.component";
import {ReporteBienRouting} from "./reporte-bien.routing";

@NgModule({
    imports: [
        ReporteBienRouting,
        CommonModule,
        FormsModule,
        MatButtonModule,
        MatCardModule,
        MatCheckboxModule,
        MatGridListModule,
        MatIconModule,
        MatInputModule,
        MatListModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatRadioModule,
        MatSidenavModule,
        MatSlideToggleModule,
        MatSelectModule,
        SelectCatalogoItemModule,
        MatTabsModule,
        MatToolbarModule,
        MatTableModule,
        BaseToolBarModule,
        SelectCarreraModule,
        PaginadorNavegacionModule,
        FechaMinMaxModule
    ],
    declarations: [
        RepPrestacionComponent,
        reporteDinamicoPipe
    ],
    providers: [
        MatIconRegistry,
        DetallePrestacionService,
        UtilService,
        ConfigService,
        ResourceService

    ]
})
export class ReporteBienModule {
}
