/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule,
    MatDatepickerModule,
    MatNativeDateModule,
	MatDividerModule,
	MatFormFieldModule
} from "@angular/material";
import {FechaMinMaxComponent} from "./fecha-min-max.component";

@NgModule({
    imports: [
        FormsModule,
        MatInputModule,
        MatButtonModule,
        MatDatepickerModule,
        MatNativeDateModule,
        MatSnackBarModule,
		MatDividerModule,
		MatFormFieldModule
    ],
    declarations: [
        FechaMinMaxComponent
    ],
    exports: [
        FechaMinMaxComponent
    ]
})

export class FechaMinMaxModule {
}
