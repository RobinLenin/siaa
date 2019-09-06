import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {BaseToolBarModule} from "../toolbar/base-toolbar.module";
import {BuscarPersonaModule} from "../../../shared/core/components/buscar-persona/buscar-persona.module";
import {BuscarPipeModule} from "../../../shared/comun/pipes/buscar/buscar.pipe.module";
import {PaginadorBuscarModule} from "./../../../shared/comun/components/paginador-buscar/paginador-buscar.module";
import {PaginadorNavegacionModule} from "../../../shared/comun/components/paginador-navegacion/paginador-navegacion.module";
import {SelectCarreraModule} from "../select-carrera/select-carrera.module";
import {SelectCatalogoItemModule} from "../../../shared/core/components/select-catalogo-item/select-item.module";
import {PlantillaImprimirModule} from "../../../shared/comun/components/plantilla-imprimir/plantilla-imprimir.module";

import {MatIconModule, MatIconRegistry,
        MatButtonModule,
        MatCardModule,
        MatCheckboxModule,
        MatGridListModule,
        MatInputModule,
        MatListModule,
        MatTableModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatRadioModule,
        MatSidenavModule,
        MatSlideToggleModule,
        MatTabsModule,
        MatToolbarModule,
        MatTooltipModule} from '@angular/material';

import {ConfigService} from "../../services/configure.service";
import {DetallePrestacionService} from "./../../services/detalle-prestacion.service";
import {NotificationService} from "../../services/notificacion.service";
import {PersonaService} from "./../../../core/services/persona.service";
import {PrestacionService} from "./../../services/prestacion.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {UtilService} from "./../../../shared/comun/services/util.service";

import {PrestacionAdminComponent} from "./prestacion-admin.component";
import {PrestacionListComponent} from "./prestacion-list.component";
import {PrestacionRouting} from "./prestacion.routing";

/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */

@NgModule({
    imports: [
        PrestacionRouting,
		PlantillaImprimirModule,
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        MatButtonModule,
        MatCardModule,
        MatCheckboxModule,
        MatGridListModule,
        MatIconModule,
        MatInputModule,
        MatListModule,
        MatTableModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatRadioModule,
        MatSidenavModule,
        MatSlideToggleModule,
        MatTabsModule,
        MatToolbarModule,
        MatTooltipModule,
        SelectCarreraModule,
        SelectCatalogoItemModule,
        BaseToolBarModule,
        PaginadorNavegacionModule,
        BuscarPipeModule,
        PaginadorBuscarModule,
        BuscarPersonaModule
    ],
    declarations: [
        PrestacionAdminComponent,
        PrestacionListComponent,
    ],
    providers: [
        MatIconRegistry,
        DetallePrestacionService,
        PrestacionService,
        ResourceService,
        ConfigService,
        UtilService,
        PersonaService,
        NotificationService
    ],
    exports: [
        PrestacionAdminComponent,
        PrestacionListComponent
    ]

})
export class PrestacionModule {
}
