/* Autor: Yazber Romero.
 * Fecha: 27/07/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        27/07/2016                   	    Implementación inicial.
 */
import {Component, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import {IPrestacionRep} from '../../dto/IPrestacionRep';
import {DetallePrestacionService} from '../../services/detalle-prestacion.service';
import {ConfigService} from '../../services/configure.service'
import {ResourceService} from '../../../shared/comun/services/resource.service'
import {FechaMinMaxComponent} from '../../../shared/comun/components/calendario/fecha-min-max.component'

import * as moment from 'moment';

@Component({
    moduleId: module.id,
    selector: 'rep-prestacion',
    templateUrl: './rep-prestacion.component.html'
})
export class RepPrestacionComponent implements OnInit {

    /*Seccion de Atributos */
    displayedColumns: string[] = ['year', 'month', 'dni', 'name', 'last_name', 'career', 'amount'];
    prestacionesRep: IPrestacionRep[] = [];
    fechaDesde: string;
    fechaHasta: string;
    isRepGeneral: boolean = false;
    carreraId: number;
    dataImprimir = {'data': [], 'tipoReporte': 0}
    tipoReporte: number = 0;
    query: string;
    servicio: string;
    token: string;
    columns = [
        {title: 'Año', dataKey: 'anio'},
        {title: 'Mes', dataKey: 'mes'},
        {title: 'DNI', dataKey: 'dni'},
        {title: 'Nombres', dataKey: 'nombres'},
        {title: 'Apellidos', dataKey: 'apellidos'},
        {title: 'Carrera', dataKey: 'carrera'},
        {title: 'Cantidad', dataKey: 'cantidad'},
    ];

    @Output() notificadorEvent = new EventEmitter();
    @Input() configuration: ConfigService;
    numberOfItems: number;
    @ViewChild(FechaMinMaxComponent)
    dateMinMaxComponent: FechaMinMaxComponent;

    constructor(private service: DetallePrestacionService,
                private config: ConfigService,
                private resource: ResourceService) {

    }

    ngOnInit() {
        this.loadPrestaciones();
    }

    /**
     * Permite cargar prestaciones
     */
    loadPrestaciones() {
        this.numberOfItems = 0;
        if (this.configuration) {
            this.config = this.configuration;
        }

        this.fechaDesde = moment(this.dateMinMaxComponent.start_dt).format('YYYY-MM-DD')
        this.fechaHasta = moment(this.dateMinMaxComponent.end_dt).format('YYYY-MM-DD')
        if (this.fechaDesde && this.fechaHasta) {
            this.service.obtenerPrestacionesCriterios(this.fechaDesde, this.fechaHasta)
                .subscribe(
                    (res) => {
                        this.prestacionesRep = res.data;
                        this.dataImprimir.data = this.prestacionesRep;
                    });
        }

    }

    /**
     * Permite soportar la seleccion del tipo de reporte desde la vista
     * @param  {number} value
     */
    selectReporte(value: number) {
        value == 1 ? this.isRepGeneral = true : this.isRepGeneral = false;
        this.dataImprimir.tipoReporte = this.tipoReporte;
        this.loadPrestaciones();
        this.notificadorEvent.emit(value);
    }

    /**
     * Permite soportar la seleccion de carrera desde la vista
     * @param  {number} idCarrera
     */
    onCarreraSelect(idCarrera: number) {
        this.carreraId = idCarrera;
        this.loadPrestaciones();
        this.notificadorEvent.emit(idCarrera);
    }

    onFechaDesdeSelect(desde: any) {
        this.fechaDesde = desde
        this.loadPrestaciones();
    }

    onFechaHastaSelect(hasta: any) {
        this.fechaHasta = hasta
        this.loadPrestaciones();
    }
}


