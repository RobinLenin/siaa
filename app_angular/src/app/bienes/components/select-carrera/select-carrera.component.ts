/* Autor: Yazber Romero.
 * Fecha: 28/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion
 * Yazber Romero      	        28/07/2016                   	    Implementación inicial.
 */
import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Carrera } from '../../../curricular/models/carrera.model';
import { CarreraService } from '../../../curricular/services/carrera.service';

@Component({
    moduleId: module.id,
    selector: 'select-carrera',
    templateUrl: 'select-carrera.component.html'
})
export class SelectCarreraComponent implements OnInit {

    @Input() carreras: Carrera[];
    @Input() selectedValue: number;
    @Input() name: string;
    @Input() isDisable: boolean = false;
	@Input() placeholder: string = 'Seleccione una opción';
    @Output() notificador = new EventEmitter();
    @Output() notificadorSeleccion = new EventEmitter();


    constructor(private service: CarreraService) { }

    ngOnInit() {
        this.loadCarreras();
    }


    /**
     * Permite cargar el listado de carreras
     */
    loadCarreras() {
        return this.service.getCarrerasVigentes().subscribe(
            resp => this.carreras = resp.data);
    }

    /**
     * Permite soporte de evento para seleccion de carrera
     * @param  {} newValue
     */
    selectCarrera(newValue) {
        newValue == null ? this.selectedValue = null:this.selectedValue = newValue;
        this.notificador.emit(this.selectedValue);
    }
}
