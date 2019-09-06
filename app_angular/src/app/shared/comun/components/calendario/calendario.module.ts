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
    MatNativeDateModule
} from "@angular/material";
import {CalendarioComponent} from "./calendario.component";

@NgModule({
    imports: [
        FormsModule,
        MatInputModule,
        MatButtonModule,
        MatDatepickerModule,
        MatNativeDateModule,
        MatSnackBarModule
    ],
    declarations: [
        CalendarioComponent
    ],
    exports: [
        CalendarioComponent
    ]
})

export class CalendarioModule {
}
