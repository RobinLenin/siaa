import { Observable } from 'rxjs/Rx';
import { MatDialogRef, MatDialog, MatDialogConfig } from '@angular/material';
import { Injectable, ViewContainerRef } from '@angular/core';
import { DialogConfirmarComponent } from '../components/dialog/dialog-confirmar.component';
import { DialogNotificacionComponent } from '../components/dialog/dialog-notificacion.component';
import { DialogImprimirComponent } from '../components/dialog/dialog-imprimir.component';
import { DialogGenericoComponent } from '../components/dialog/dialog-generico.component';

@Injectable()
export class DialogService {


    constructor(private dialog: MatDialog) { }

    /**
     * @desc Muestra el dialog para confirmar una petición. El parametro
     * viewContainerRef es opcional
     * @returns {MatDialogRef<any>}
     */
    public confirm(title: string, message: string, viewContainerRef: ViewContainerRef=null): Observable<boolean> {
        let dialogConfig= this.getConfigDialog(viewContainerRef);
        let dialogRef = this.getDialog(dialogConfig, DialogConfirmarComponent);
        dialogRef.componentInstance.title = title;
        dialogRef.componentInstance.message = message;
        return dialogRef.afterClosed();
    }

    /**
     * @desc Muestra el dialog para mostrar una notificación. El parametro
     * viewContainerRef es opcional
     * @returns {MatDialogRef<any>}
     */
    public notificacion(title: string, message: string, viewContainerRef: ViewContainerRef=null): Observable<boolean> {
        let dialogConfig= this.getConfigDialog(viewContainerRef);
        let dialogRef = this.getDialog(dialogConfig, DialogNotificacionComponent);
        dialogRef.componentInstance.title = title;
        dialogRef.componentInstance.message = message;
        return dialogRef.afterClosed();
    }

    /**
     * @desc Muestra el dialog para mostrar dos opciones de impresión, horizontal y vertical. El parametro
     * viewContainerRef es opcional
     * @returns {MatDialogRef<any>}
     */
    public imprimir(title: string, message: string, viewContainerRef: ViewContainerRef=null): Observable<boolean> {
        let dialogConfig= this.getConfigDialog(viewContainerRef);
        let dialogRef = this.getDialog(dialogConfig, DialogImprimirComponent);
        dialogRef.componentInstance.title = title;
        dialogRef.componentInstance.message = message;
        return dialogRef.afterClosed();
    }

    /**
     * @desc Muestra el dialog para confirmar una petición. El parametro
     * viewContainerRef es opcional
     * @returns {MatDialogRef<any>}
     */
    public generic(title: string, message: string, botones: string[], viewContainerRef: ViewContainerRef=null): Observable<boolean> {
        let dialogConfig= this.getConfigDialog(viewContainerRef);
        let dialogRef = this.getDialog(dialogConfig, DialogGenericoComponent);
        dialogRef.componentInstance.title = title;
        dialogRef.componentInstance.message = message;
        dialogRef.componentInstance.botones = botones;
        return dialogRef.afterClosed();
    }

    /**
     * @desc Crea el dialog con la configuración recibida como parámetro
     * @returns {MatDialogRef<any>}
     */
    public getDialog(mdDialogConfig, dialogComponent){
        let dialogRef: MatDialogRef<any>;
        dialogRef = this.dialog.open(dialogComponent, mdDialogConfig);
        return dialogRef
    }

    /**
     * @desc Configuración por defecto del Dialog ha ser mostrado
     * @returns {MatDialogRef<any>}
     */
    public getConfigDialog(viewContainerRef:ViewContainerRef){
        let config = new MatDialogConfig();
        config.viewContainerRef = viewContainerRef;
        config.disableClose = true;
    }
}
