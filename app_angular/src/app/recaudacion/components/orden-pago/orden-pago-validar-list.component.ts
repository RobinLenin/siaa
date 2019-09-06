import {Component, OnInit} from "@angular/core";
import {ActivatedRoute, Router} from "@angular/router";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {OrdenPago} from "../../models/orden-pago.model";
import {DetalleParametrizacionEnum, ComunEnum} from "../../../shared/comun/utils/enums";
import {appService} from "../../../credentials";



@Component({
    moduleId: module.id,
    selector: 'recuadacion-orden-pago-validar-list',
    templateUrl: './orden-pago-validar-list.component.html'
})

export class OrdenPagoValidarListComponent implements OnInit {

    activarEditar: boolean;
    activarBuscador: boolean;
    botones = {
        showIniciar: true,
        showEditar: true,
        showBuscador: true
    };
    displayedColumns: string[] = [
        'accion', 'cliente', 'identificacion', 'fecha_emision', 'estado', 'descripcion'
    ];
    ordenesPago: OrdenPago [] = [];
    ordenesPagoSeleccionado: OrdenPago;
    servicio: string;
    filtro: string;
    itemsPorPagina: number;
    pagina: number;

    constructor(private route: ActivatedRoute,
                private router: Router,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Función inicializadora del componente
     */
    ngOnInit() {
        this.activarEditar = false;
        this.activarBuscador = false;
        this.filtro = '';
        this.pagina = 1;
        this.ordenesPagoSeleccionado = null;
        this.itemsPorPagina = Number(localStorage.getItem(DetalleParametrizacionEnum.ROWS_TABLE))
        this.servicio = appService.ws_recaudacion_ordenes_pago_paginacion;
    }

    /**
     * @desc Función que inicializa las variables y las lista de pagos.
     */
    initPagos() {
        this.ngOnInit();
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
     * @desc Función que verifica si el item esta o no seleccionada
     */
    esItemSeleccionado(item) {
        return item == this.ordenesPagoSeleccionado;
    }

    /**
     * @desc Función que selecciona un item y activa el boton editar
     */
    selectedItem(item: OrdenPago) {
        if (item == this.ordenesPagoSeleccionado) {
            this.ordenesPagoSeleccionado = null;
            this.activarEditar = false
        } else {
            this.ordenesPagoSeleccionado = item;
            this.activarEditar = true
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
     * @desc Función que navega la detalle de la orden de pago para validar
     */
    validarPago() {
        let link = ['../recaudacion-orden-pago-validar-detail', this.ordenesPagoSeleccionado.id];
        this.router.navigate(link, {relativeTo: this.route});
    }
}
