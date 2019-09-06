import {Component, OnInit, ViewContainerRef} from "@angular/core";
import {Router, ActivatedRoute} from "@angular/router";
import {PuntoEmisionService} from "../../services/punto-emision.service";
import {DialogService} from "../../../shared/comun/services/dialog.service";
import {UtilService} from "../../../shared/comun/services/util.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {OrdenPago} from "../../models/orden-pago.model";
import {PuntoEmisionUAA} from "../../models/punto-emision-uaa.model";
import {DetalleParametrizacionEnum, ComunEnum} from "../../../shared/comun/utils/enums";
import {appService} from "../../../credentials";

@Component({
    moduleId: module.id,
    selector: 'recaudacion-orden-pago-list',
    templateUrl: './orden-pago-list.component.html'
})

export class OrdenPagoListComponent implements OnInit {

    displayedColumns = ['accion', 'codigo', 'secuencial', 'fecha_emision', 'estado', 'cliente', 'identificacion', 'referencia'];
    activarEditar: boolean = false;
    activarBuscador: boolean = false;
    puntoEmisionUaa: PuntoEmisionUAA;
    puntosEmisionUaa: PuntoEmisionUAA [] = [];
    ordenesPago: OrdenPago[] = [];
    ordenesPagoSelec: OrdenPago[] = [];
    filtro: string;
    pagina: number;
    itemsPorPagina: number;
    servicio: string;
    botones = {
        showIniciar: true,
        showCrear: true,
        showEditar: true,
        showBuscador: true
    };

    constructor(private router: Router,
                private route: ActivatedRoute,
                private puntoEmisionService: PuntoEmisionService,
                private dialogService: DialogService,
                private utilService: UtilService,
                private viewContainerRef: ViewContainerRef,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Función inicializadora del
     * componente
     */
    ngOnInit() {
        this.puntoEmisionService.getPuntosEmisionUaaInFuncionario(window.localStorage.getItem('auth_key')).subscribe(resp => {
            if (resp.status == 200) {
                this.puntosEmisionUaa = <PuntoEmisionUAA[]>resp.data;
                if (localStorage.getItem("puntoEmisionUaa")) {
                    let puntoEmisionUaa = JSON.parse(localStorage.getItem("puntoEmisionUaa"));
                    for (let i in this.puntosEmisionUaa) {
                        if (this.puntosEmisionUaa[i].id == puntoEmisionUaa.id) {
                            this.puntoEmisionUaa = this.puntosEmisionUaa[i];
                            break;
                        }
                    }
                    this.initVariables();
                }
            } else {
                this.dialogService.notificacion('ERROR!', resp.message, this.viewContainerRef);
            }

        });
    }

    /**
     * @desc Función que inicializa las variables del consumo del API y
     * obtiene las ordenes de pago para el punto de emisión UAA del funcionario
     */
    initVariables() {
        if (this.puntoEmisionUaa) {
            this.filtro = '';
            this.pagina = 1;
            this.itemsPorPagina = Number(localStorage.getItem(DetalleParametrizacionEnum.ROWS_TABLE));
            this.servicio = appService.ws_recaudacion_ordenes_pago_paginacion + '?punto_emision_uaa_id=' + this.puntoEmisionUaa.id
            this.activarBuscador = false;
            this.ordenesPagoSelec = [];
            this.changeBotones(this.ordenesPagoSelec.length);
        }
    }

    /**
     * @desc Función que reinicia los valores de las variables a suestado inicial. El obtener
     * la lista de items solo se requiere cuando deseamos que el boton ACTUALIZAR cargue
     * nuevamente con los valores por defecto
     */
    getOrdenesPago() {
        this.initVariables();
        this.resourceService.getObjectsPagination(
            this.servicio, localStorage.getItem(ComunEnum.AUTH_KEY),
            this.pagina, this.itemsPorPagina, this.filtro)
            .subscribe(res => {
                if (res.status == 200) {
                    this.ordenesPago = res.data;
                }
            });
    }

    /**
     * @desc Función que llama al componente que permite
     * crear una Orden de Pago, orden-pago-detail.component
     */
    crear() {
        localStorage.setItem('puntoEmisionUaa', JSON.stringify(this.puntoEmisionUaa));
        let link = ['../recaudacion-orden-pago-detail', 0];
        this.router.navigate(link, {relativeTo: this.route});
    }

    /**
     * @desc Función que llama al componente que permite
     * editar una Orden de Pago, orden-pago-detail.component
     */
    editar() {
        localStorage.setItem('puntoEmisionUaa', JSON.stringify(this.puntoEmisionUaa));
        let link = ['../recaudacion-orden-pago-detail', this.ordenesPagoSelec[0]['id']];
        this.router.navigate(link, {relativeTo: this.route});
    }

    /**
     * @desc Función que almacena los items seleccionados para proceder
     * a ejecutar las operaciones definidas (editar, anular)
     * @param {OrdenPago} item - Orden de pago a insertar o a eliminar
     */
    selectedItem(item: OrdenPago) {
        var idx = this.ordenesPagoSelec.indexOf(item);
        if (idx > -1) {
            this.ordenesPagoSelec.splice(idx, 1);
        } else {
            this.ordenesPagoSelec.push(item);
        }
        this.changeBotones(this.ordenesPagoSelec.length)
    }

    /**
     * @desc Función que verifica si el item esta o no seleccionada
     */
    esItemSeleccionado(item) {
        return this.utilService.existeItemPorId(item, this.ordenesPagoSelec);
    }

    /**
     * @desc Función que actualiza la variable
     * que contiene el estado para mostrar el filtro
     * de buscar en la tabla
     */
    changeBuscador() {
        this.activarBuscador ? this.activarBuscador = false : this.activarBuscador = true;
    }

    /**
     * @desc Función que actualiza las variables que
     * contiene el estado para editar y anular un item
     * @param {Number} item - número de items seleccionados
     */
    changeBotones(tamanio) {
        if (tamanio == 0) {
            this.activarEditar = false;
        } else if (tamanio == 1) {
            this.activarEditar = true;
        } else {
            this.activarEditar = false;
        }
    }

}
