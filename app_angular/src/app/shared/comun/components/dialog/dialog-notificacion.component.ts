import { Component }    from '@angular/core';
import { MatDialogRef } from '@angular/material';

@Component({
    moduleId: module.id,
    selector: 'dialog-notificacion',
    template: `
        <h1 mat-dialog-title>{{ title }}</h1>
        <mat-dialog-content>{{ message }}</mat-dialog-content>
        <mat-dialog-actions>
            <button type="button" color="primary" mat-raised-button  (click)="dialogRef.close()">Aceptar</button>
        </mat-dialog-actions>
    `
})

export class DialogNotificacionComponent  {

    public title: string;
    public message: string;

    constructor(public dialogRef: MatDialogRef<DialogNotificacionComponent>) {

    }


}
