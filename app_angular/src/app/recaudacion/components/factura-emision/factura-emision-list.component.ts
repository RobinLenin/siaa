import {Component, OnInit, ViewContainerRef, ViewChildren} from "@angular/core";
import {OrdenPagoService} from "../../services/orden-pago.service";
import {DialogService} from "../../../shared/comun/services/dialog.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {PuntoEmisionService} from '../../services/punto-emision.service';
import {ComunEnum} from "../../../shared/comun/utils/enums";
import {appService} from "../../../credentials";
import {HomeComponent} from "../../../home/home.component";
import * as moment from "moment";

@Component({
    moduleId: module.id,
    selector: 'factura-emision-list',
    templateUrl: './factura-emision-list.component.html'
})

export class FacturaEmisionListComponent implements OnInit {

    activarBuscador: boolean;
    selecTodos: boolean = false;
    consumidorFinal = '9999999999999';
    tipoAccion: string = 'EMITIR';
    query: string;
    fechaDesde: Date;
    fechaHasta: Date;
    facturasEmitir: any[] = [];
    facturasEmitirTipo = [];
    facturasEmitirSelec = [];
    puntosEmision = [];
    puntoEmision;
    botones = {showIniciar: true, showBuscador: true};

    @ViewChildren('itemsFilter') facturasEmitirFilter;

    constructor(private ordenPagoService: OrdenPagoService,
                private puntosemisionService: PuntoEmisionService,
                private dialogService: DialogService,
                private viewContainerRef: ViewContainerRef,
                private resourceService: ResourceService,
                private homeComponent: HomeComponent) {
        this.puntosemisionService.getPuntosEmisionActivo(window.localStorage.getItem('auth_key'))
            .subscribe(res => {
                if (res.status == 200) {
                    this.puntosEmision = res.data
                } else {
                    this.dialogService.notificacion('ERROR!', res.message, this.viewContainerRef)
                }
            })

    }

    /**
     * @desc Función inicializadora del
     * componente
     */
    ngOnInit() {
        this.activarBuscador = false;
        this.query = '';
        this.fechaDesde = new Date();
        this.fechaHasta = new Date();
        this.facturasEmitir = [];
        this.facturasEmitirTipo = [];
        this.facturasEmitirSelec = [];
        this.facturasEmitirFilter = this.facturasEmitir;
    }

    /**
     * @desc Función que obtienen la lista de facturas que son generadas
     * a partir de la fecha y ordenes de pago emitidas.
     */
    generarFacturas() {
        if (this.puntoEmision && moment(this.fechaDesde).isValid() && moment(this.fechaHasta).isValid()) {

            let desde = moment(this.fechaDesde).format('YYYY-MM-DD');
            let hasta = moment(this.fechaHasta).format('YYYY-MM-DD');
            this.homeComponent.cambioEstadoCargando();
            this.changeTipoAccion();

            if (this.tipoAccion == 'EMITIR') {
                this.ordenPagoService.getFacturasEmitir(window.localStorage.getItem('auth_key'), desde, hasta, this.puntoEmision)
                    .subscribe(res => {
                        if (res.status == 200) {
                            this.facturasEmitir = res.data;
                            if (res.message && res.data.length != 0) {
                                this.dialogService.notificacion('ADVERTENCIA!', res.message, this.viewContainerRef)
                            }
                        } else {
                            this.facturasEmitir = []
                            this.dialogService.notificacion('ERROR!', res.message, this.viewContainerRef)
                        }
                        this.facturasEmitirFilter = this.facturasEmitir;
                        this.getListaTipoFactura();
                        this.homeComponent.cambioEstadoCargando();
                    });
            } else {
                this.ordenPagoService.getFacturasEmitidas(window.localStorage.getItem('auth_key'), desde, hasta)
                    .subscribe(res => {
                        if (res.status == 200) {
                            this.facturasEmitir = res.data;
                            if (res.message && res.data.length != 0) {
                                this.dialogService.notificacion('ADVERTENCIA!', res.message, this.viewContainerRef)
                            }
                        } else {
                            this.facturasEmitir = []
                            this.dialogService.notificacion('ERROR!', res.message, this.viewContainerRef)
                        }
                        this.facturasEmitirFilter = this.facturasEmitir;
                        this.homeComponent.cambioEstadoCargando();
                    });
            }
        }
    }

    /**
     * @desc Ejecuta la acción correspondiente
     */
    confirmarGuardarAccion() {
        if (this.tipoAccion == 'EMITIR' && this.facturasEmitir.length) {
            let msg = '¿Seguro desea guardar ' + this.facturasEmitir.length + ' registro(s) de facturas generadas en pantalla?'
            this.dialogService.confirm('FACTURAS GENERADAS DE LAS ORDENES DE PAGO', msg, this.viewContainerRef)
                .subscribe(res => {
                    if (res == true) {
                        this.emitirFacturas();
                    }
                });

        } else if (this.tipoAccion == 'ANULAR' && this.facturasEmitirSelec.length) {
            let msg = '¿Seguro desea ANULAR ' + this.facturasEmitirSelec.length + ' registro(s) de facturas?'
            this.dialogService.confirm('ANULAR FACTURAS', msg, this.viewContainerRef)
                .subscribe(res => {
                    if (res == true) {
                        this.anularFacturas();
                    }
                });
        }
    }

    /**
     * @desc Función para anula las facturas
     * generadas a partir de las ordenes de pago
     */
    anularFacturas() {
        if (this.facturasEmitirSelec) {
            this.ordenPagoService.anularFacturas(window.localStorage.getItem('auth_key'), this.facturasEmitirSelec)
                .subscribe(res => {
                    if (res.status == 200) {
                        this.dialogService.notificacion('ÉXITO!', res.message, this.viewContainerRef).subscribe(() => {
                            this.generarFacturas();
                        });
                    } else {
                        this.dialogService.notificacion('ERROR', res.message, this.viewContainerRef)
                    }
                });
        }
    }

    /**
     * @desc Función que guarda las facturas generadas a partir
     * de la fecha y ordenes de pago emitidas.
     */
    emitirFacturas() {
        if (this.facturasEmitir) {
            let data = {
                'punto_emision': this.puntoEmision,
                'documentos_a_emitir': this.facturasEmitir
            }
            this.ordenPagoService.guardarFacturasEmitir(window.localStorage.getItem('auth_key'), data)
                .subscribe(res => {
                    if (res.status == 200) {
                        this.dialogService.notificacion('ÉXITO!', 'Las facturas generadas de las Ordenes de Pago han sido almacenadas con éxito', this.viewContainerRef).subscribe(() => {
                            this.generarFacturas();
                        });
                    } else {
                        this.dialogService.notificacion('ERROR', res.message, this.viewContainerRef)
                    }
                });
        }
    }

    /**
     * @desc Función que actualiza la variable que
     * muestra el  filtro para buscar coincidencias
     */
    changeBuscador() {
        this.activarBuscador = this.activarBuscador ? false : true;
    }

    /**
     * @desc Función para visualizar la factura previa a ser
     * guardada en la BD
     */
    verPreviaFactura(item) {
        let token = localStorage.getItem(ComunEnum.AUTH_KEY);
        this.resourceService.printObjetoBlobPorPost(appService.ws_recaudacion_factura_reporte_detalle, item, token)
    }

    /**
     * @desc Función para visualizar reporte consolidado de las
     * facturas previas, que fueron generadas a partir de las ordenes de pago
     */
    verConsolidadoFacturas() {
        let token = localStorage.getItem(ComunEnum.AUTH_KEY);
        let data = {};
        data['documentos_a_emitir'] = this.facturasEmitir;
        data['fecha_desde'] = moment(this.fechaDesde).format('YYYY-MM-DD');
        data['fecha_hasta'] = moment(this.fechaHasta).format('YYYY-MM-DD');
        this.resourceService.printObjetoBlobPorPost(appService.ws_recaudacion_factura_reporte_generadas, data, token, this.homeComponent);
    }

    /**
     * @desc Función que contabiliza el total por tipos
     * de facturas (Individual, Consumidor final.....)
     */
    getListaTipoFactura() {
        let consumidor_final = 0;
        let individual = 0;
        for (let i in this.facturasEmitir) {
            if (this.facturasEmitir[i].persona.numero_documento == this.consumidorFinal){
                consumidor_final += 1
            }else{
                individual += 1
            }
        }
        this.facturasEmitirTipo = [
            {nombre: 'Individual', total: individual},
            {nombre: 'Consumidor final', total:consumidor_final}
        ]
    }

    /**
     * @desc Función inicializa los datos cuando se cambia de acción ajecutar
     */
    changeTipoAccion() {
        this.facturasEmitir = [];
        this.facturasEmitirTipo = [];
        this.facturasEmitirSelec = [];
    }

    /**
     * @desc Función que almacena los items
     * seleccionados para proceder a ejecutar
     * las operaciones definidas
     * @param item - objeto a insertar o eliminar de la lista de seleccionados
     */
    selectedItem(item) {
        var idx = this.facturasEmitirSelec.indexOf(item);
        if (idx > -1) {
            this.facturasEmitirSelec.splice(idx, 1);
        } else {
            this.facturasEmitirSelec.push(item);
        }
    }

    /**
     * @desc Función que selecciona/deselecciona todos los items de las facturas
     */
    selectedTodos() {
        this.facturasEmitirSelec = [];
        if (this.selecTodos) {
            for (let i in this.facturasEmitir) {
                this.selectedItem(this.facturasEmitir[i]);
            }
        }
    }

    /**
     * @desc Verifica si el item esta seleccionado
     */
    esItemSeleccionado(item) {
        return this.facturasEmitirSelec.indexOf(item) > -1;
    }
}
