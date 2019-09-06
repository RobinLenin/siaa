/* Autor: Yazber Romero.
 * Fecha: 11/08/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        Fecha: 11/08/2016                   	    Implementación inicial.
 */
import {Output, Input, OnInit, Component, EventEmitter} from "@angular/core";
import {MatSnackBar} from "@angular/material";
import * as moment from "moment";

@Component({
    moduleId: module.id,
    selector: 'calendario',
    templateUrl: 'calendario.component.html'
})

export class CalendarioComponent implements OnInit {

    @Output() notificador = new EventEmitter();
    @Input() placeholder: string = '';
    @Input() required: boolean = false;
    @Input() disabled: boolean = false;
    @Input() start_dt: string = '';
    @Input() formatoInicial: string='YYYY-MM-DD HH:mm:ss'; // Si no se ubica HH:mm:ss, se ubica la fecha un dia anterior(esperar mejoras de datepicker)
    @Input() formatoRetornar: string='YYYY-MM-DD';
    fecha: Date;

    constructor(private snackBar: MatSnackBar) {
    }

    ngOnInit() {
        if (this.start_dt){
            let fechaAux = moment(this.start_dt).format(this.formatoInicial);
            this.fecha = new Date(fechaAux);
        }
    }

    changeInputFecha() {
        if (moment(this.fecha).isValid()) {
            let fechaAux = moment(this.fecha).format(this.formatoRetornar);
            this.notificador.emit(fechaAux);
        }else{
            this.notificador.emit(this.fecha);
            this.openSnackBar()
        }
    }

    openSnackBar() {
        this.snackBar.open('Formato de fecha inválida', 'Aceptar', {
                duration: 5000
        });

    }

}