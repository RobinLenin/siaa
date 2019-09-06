/* Autor: Yazber Romero.
 * Fecha: 11/08/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        Fecha: 11/08/2016                   	    Implementación inicial.
 */
import {Component, OnInit, Output, EventEmitter, Input} from "@angular/core";
import * as moment from "moment";
import {MatSnackBar} from "@angular/material";

@Component({
    moduleId: module.id,
    selector: 'fecha-min-max',
    templateUrl: 'fecha-min-max.component.html',
})

export class FechaMinMaxComponent implements OnInit {

    @Output() fechaDesde = new EventEmitter();
    @Output() fechaHasta = new EventEmitter();
    @Input() start_dt: Date;
    @Input() end_dt: Date;
    @Input() placeholder_desde: string = '';
    @Input() placeholder_hasta: string = '';

    constructor(private snackBar: MatSnackBar) {
    }

    ngOnInit() {}

    changeInputDesde(value) {
        this.fechaDesde.emit(this.start_dt);
        if(!moment(this.start_dt).isValid()){
            this.openSnackBar();
        }
    }

    changeInputHasta(value) {
        this.fechaHasta.emit(this.end_dt);
        if(!moment(this.end_dt).isValid()){
          this.openSnackBar();
        }
    }

    openSnackBar() {
        this.snackBar.open('Formato de fecha inválida', 'Aceptar', {
                duration: 5000
        });

    }
}

