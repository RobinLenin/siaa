/* Autor: Yazber Romero.
 * Fecha: 22/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        22/07/2016                   	    Implementación inicial.
 */
import {Component, OnInit, EventEmitter, Output, Input} from "@angular/core";
import {UtilService} from "../../../comun/services/util.service";
import {Persona} from "../../../../core/models/persona.model";
import {DetalleParametrizacionEnum} from "../../../comun/utils/enums";
import {appService} from "../../../../credentials";


@Component({
    moduleId: module.id,
    selector: 'buscar-persona',
    templateUrl: 'buscar-persona.component.html'
})
export class BuscarPersonaComponent implements OnInit {

    personas: Persona[] = [];
    personasSeleccionadas: Persona[] = [];
    itemsPorPagina: number = 0;
    filtro: string;
    servicio: string;
    pagina: number;
    esVisible: boolean = false;

    @Input() myStyles: any = {};
    @Input() variosSeleccion: boolean = true;
    @Input() disabled: boolean = false;
    @Input() placeholder: string = 'Buscar';
    @Output() notificadorSeleccion = new EventEmitter();
    @Output() notificadorEnter = new EventEmitter();

    constructor(private utilService: UtilService) {
    }

    ngOnInit() {
        this.filtro = '';
        this.itemsPorPagina = Number(localStorage.getItem(DetalleParametrizacionEnum.ROWS_TABLE))
        this.servicio = appService.ws_core_persona_lista_paginacion;
    }

    /**
     * Permite insertar o eliminar un registro de usuario
     * en la lista de usuarios seleccionados
     */
    itemSeleccionado(item, list) {
        if (list.length > 0) {
            var idx = list.indexOf(item);
            if (idx > -1) {
                list.splice(idx, 1);
            } else {
                list.push(item);
                this.seleccionarVarios(list)
            }
        } else {
            list.push(item);
            this.seleccionarVarios(list)
        }
        this.notificadorSeleccion.emit(list);
    }

    /**
     * Verifica si existe el registro de persona en la lista
     */
    esItemSeleccionado(item, list) {
        return this.utilService.existeItemPorId(item, list);
    }

    /**
     * Función que cierra la ventana de usuarios si isMultiplicy es igual a 1.
     * Lo que equivale a seleccionar un solo registro de persona.
     */
    seleccionarVarios(list) {
        if (this.variosSeleccion == false && list.length == 1) {
            this.cambioFiltro('');
        }
    }

    /**
     * Permite manejar el evento de input y mostras los resultados
     */
    cambioFiltro(valor) {
        this.personasSeleccionadas = [];
        this.filtro = valor;
        if (valor !== '' && valor.length > 4) {
            this.esVisible = true;
        } else {
            this.esVisible = false;
        }
    }

    enterInputSearch(texto) {
        this.notificadorEnter.emit(texto);
        this.esVisible = false;
    }
}
