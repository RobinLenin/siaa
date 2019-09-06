import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material';

@Component({
    moduleId: module.id,
    selector: 'dialog-generico',
    templateUrl: './dialog-generico.component.html'
})

export class DialogGenericoComponent implements OnInit {

    public title: string;
    public message: string;
    public botones: string[];
    private btn: any;

    constructor(public dialogRef: MatDialogRef<DialogGenericoComponent>) {
    }
    ngOnInit() {

    }

}

