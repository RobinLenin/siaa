import { NgModule } from '@angular/core';
import {CommonModule} from "@angular/common";
import { MatDialogModule, MatButtonModule}    from '@angular/material';
import { DialogConfirmarComponent } from './dialog-confirmar.component';
import { DialogNotificacionComponent } from './dialog-notificacion.component';
import { DialogImprimirComponent } from './dialog-imprimir.component';
import { DialogGenericoComponent } from './dialog-generico.component';
import { DialogService } from "../../services/dialog.service";

@NgModule(
    {   imports: [
        CommonModule,
        MatDialogModule,
        MatButtonModule,
    ],
     exports: [
         DialogConfirmarComponent,
         DialogNotificacionComponent,
         DialogImprimirComponent,
         DialogGenericoComponent
     ],
     providers: [
         DialogService
     ],
     declarations: [
         DialogConfirmarComponent,
         DialogNotificacionComponent,
         DialogImprimirComponent,
         DialogGenericoComponent
     ],
     entryComponents: [
         DialogConfirmarComponent,
         DialogNotificacionComponent,
         DialogImprimirComponent,
         DialogGenericoComponent
     ],
    }
)
export class DialogModule { }
