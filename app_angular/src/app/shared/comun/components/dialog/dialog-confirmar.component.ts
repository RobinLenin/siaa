import { Component }    from '@angular/core';
import { MatDialogRef } from '@angular/material';

@Component({
    moduleId: module.id,
    selector: 'dialog-confirmar',
    template: `
        <h1 mat-dialog-title>{{ title }}</h1>
        <mat-dialog-content>{{ message }}</mat-dialog-content>
        <mat-dialog-actions>
            <button type="button" mat-raised-button color="primary"
            (click)="dialogRef.close(true)">Aceptar</button>
            <button type="button" mat-button 
                (click)="dialogRef.close()">Cancelar</button>
        </mat-dialog-actions>  
    `
})

export class DialogConfirmarComponent  {

    public title: string;
    public message: string;

    constructor(public dialogRef: MatDialogRef<DialogConfirmarComponent>) {

    }


}

