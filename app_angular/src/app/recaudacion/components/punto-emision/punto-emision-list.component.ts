import {Component, OnInit, ViewContainerRef} from '@angular/core';
import {Router, ActivatedRoute} from '@angular/router';

import {PuntoEmisionService} from '../../services/punto-emision.service'
import {DialogService} from '../../../shared/comun/services/dialog.service';
import {PuntoEmision} from '../../models/punto-emison.model'

@Component({
    moduleId: module.id,
    selector: 'punto-emision-list',
    templateUrl: './punto-emision-list.component.html'
})
export class PuntoEmisionListComponent implements OnInit {

    displayedColumns: string[] = ['action', 'codigo_establecimiento', 'descripcion', 'nro_desde', 'nro_hasta', 'nro_secuencial', 'activo'];
    activarBuscador: boolean;
    activarEditar: boolean;
    activarEliminar: boolean;
    query: string;
    punto_emision: PuntoEmision [] = []
    puntoEmisionSeleccionados: PuntoEmision[]
    botones = {
        showIniciar: true,
        showCrear: true,
        showEditar: true,
        showEliminar: true,
        showBuscador: true
    }

    constructor(private puntosemisionService: PuntoEmisionService,
                private router: Router,
                private route: ActivatedRoute,
                private dialogService: DialogService,
                private viewContainerRef: ViewContainerRef) {

    }

    /**
     * @desc Función inicializadora
     */
    ngOnInit() {
        this.initVariables();
        this.getPuntosEmision();
    }

    /**
     * @desc Función inicializadora del
     * variables
     */
    initVariables() {
        this.activarEditar = false;
        this.activarEliminar = false;
        this.activarBuscador = false;
        this.query = '';
        this.puntoEmisionSeleccionados = []
    }

    /**
     * @desc Función que obtiene la lista de puntos de emision
     */
    getPuntosEmision() {
        this.puntosemisionService.getPuntosEmision(window.localStorage.getItem('auth_key'))
            .subscribe(res => {
                if (res.status == 200) {
                    this.punto_emision = <PuntoEmision[]>res.data
                }
            })
    }

    /**
     * @desc Función que almacena los items
     * seleccionados para proceder a ejecutar
     * las operaciones definidas (delete, edit)
     * @param {Punto de Emision} item
     */
    selectedItem(item: PuntoEmision) {
        var idx = this.puntoEmisionSeleccionados.indexOf(item);
        if (idx > -1) {
            this.puntoEmisionSeleccionados.splice(idx, 1);
        } else {
            this.puntoEmisionSeleccionados.push(item);
        }
        this.changeBotones(this.puntoEmisionSeleccionados.length)
    }

    /**
     * @desc Función que busca el identificador del item
     * que esta en una posición
     * @param {Number} posicion
     * @returns {Number} id del item
     */
    getItemId(posicion) {
        return this.puntoEmisionSeleccionados.length > posicion ? this.puntoEmisionSeleccionados[posicion].id : 0
    }

    /**
     * @desc Función que llama al componente que permite
     * crear un item, punto-emision-detail.component
     */
    crear() {
        let link = ['../recaudacion-punto-emision-detail', 0];
        this.router.navigate(link, {relativeTo: this.route});
    }

    /**
     * @desc Función que llama al componente que permite
     * editar un item, punto-emision-detail.component
     */
    editar() {
        let link = ['../recaudacion-punto-emision-detail', this.getItemId(0)];
        this.router.navigate(link, {relativeTo: this.route});
    }

    /**
     * @desc Función para confirmar si desea eliminar
     * un o varios Puntos de Emisión
     */
    confirmarEliminarPuntoEmision() {
        this.dialogService.confirm('ELIMINACIÓN DE PUNTO(S) DE EMISIÓN', '¿Seguro desea eliminar el/los Punto(s) de Emisión seleccionadas?', this.viewContainerRef)
            .subscribe(res => {
                if (res == true) {
                    this.eliminar()
                }
            });
    }

    /**
     * @desc Función que elimina uno o varios
     * puntos de emision
     */
    eliminar() {
        let deleteExit = 0
        let deleteError = 0
        let msg = '';
        for (let item in this.puntoEmisionSeleccionados) {
            this.puntosemisionService.deletePuntoEmision(window.localStorage.getItem('auth_key'), this.getItemId(item))
                .subscribe(res => {
                    res.status == 200 ? deleteExit += 1 : deleteError += 1
                    msg += res.message + '\n'
                    if ((deleteExit + deleteError) == this.puntoEmisionSeleccionados.length) {
                        this.dialogService.notificacion('ELIMINACIÓN DE PUNTO(S) DE EMISIÓN', msg, this.viewContainerRef)
                            .subscribe(() => {
                                this.ngOnInit()
                            });
                    }
                })
        }
    }

    /**
     * @desc Función que actualiza la variable
     * que contiene el estado para mostrar el filtro
     * de la tabla
     */
    changeBuscador() {
        this.activarBuscador ? this.activarBuscador = false : this.activarBuscador = true;
    }

    /**
     * @desc Función que actualiza las variables que
     * contiene el estado para editar y eliminar un item
     * @param {Number} item - número de items seleccionados
     */
    changeBotones(tamanio) {
        if (tamanio == 0) {
            this.activarEliminar = false;
            this.activarEditar = false;
        } else if (tamanio == 1) {
            this.activarEliminar = true;
            this.activarEditar = true;
        } else {
            this.activarEliminar = true;
            this.activarEditar = false;
        }
    }
}
