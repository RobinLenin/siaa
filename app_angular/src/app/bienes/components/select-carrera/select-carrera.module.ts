/* Autor: Yazber Romero.
 * Fecha: 28/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion
 * Yazber Romero      	        28/07/2016                   	    Implementación inicial.
 */
import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";

import {MatButtonModule,
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
        MatTabsModule,
        MatToolbarModule,
        MatIconRegistry,
} from '@angular/material';

import {SelectCarreraComponent} from "./select-carrera.component";
import {CarreraService} from "../../../curricular/services/carrera.service";


@NgModule({
    imports: [
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
        MatTabsModule,
        MatToolbarModule,

    ],
    declarations: [
        SelectCarreraComponent
    ],
    providers: [
        MatIconRegistry,
        CarreraService,
    ],
    exports: [
        SelectCarreraComponent
    ],


})
export class SelectCarreraModule {
}
