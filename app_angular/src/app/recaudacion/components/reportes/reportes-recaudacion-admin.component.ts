import {Component, OnInit} from "@angular/core";
import {PuntoEmisionService} from "../../services/punto-emision.service";
import {DialogService} from "../../../shared/comun/services/dialog.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {PuntoEmision} from "../../models/punto-emison.model";
import {appService} from "../../../credentials";
import {ComunEnum} from "../../../shared/comun/utils/enums";
import * as moment from "moment";
import {ProductoService} from "../../services/producto.service";
import {Producto} from "../../models/producto.model";
import {BuscarPipe} from "../../../shared/comun/pipes/buscar/buscar.pipe";
import {HomeComponent} from "../../../home/home.component";

@Component({
    moduleId: module.id,
    selector: 'reportes-recaudacion-admin',
    templateUrl: 'reportes-recaudacion.component.html'
})

export class ReportesRecaudacionAdminComponent implements OnInit {

    fechaDesde: Date;
    fechaHasta: Date;
    puntoEmision: PuntoEmision;
    puntosEmision: PuntoEmision[];
    productos: Producto[];
    public productosBuscados: Producto[];
    producto: Producto;
    tipoReporte: any;
    tipoFormato: string = "pdf"; //pdf|excel
    listaTipoReporte: any = [];
    botones = {showIniciar: true};

    constructor(private puntosemisionService: PuntoEmisionService,
                private resourceService: ResourceService,
                private dialogService: DialogService,
                private productoService: ProductoService,
                private homeComponent: HomeComponent) {
    }

    /**
     * @desc Función inicializadora del
     * componente
     */
    ngOnInit() {
        this.puntoEmision = undefined;
        this.tipoReporte = undefined;
        this.producto = undefined;
        this.fechaDesde = new Date();
        this.fechaHasta = new Date();
        this.puntosemisionService.getPuntosEmisionActivo(window.localStorage.getItem('auth_key')).subscribe(res => {
            if (res.status == 200) {
                this.puntosEmision = res.data;
                if (this.puntosEmision.length > 0) {
                    this.listaTipoReporte = [
                        {
                            id: 1, nombre: 'Reporte de Facturas que han sido generadas',
                            url: appService.ws_recaudacion_factura_reporte_guardadas
                        },
                        {
                            id: 2, nombre: 'Reporte Consolidado de Ordenes de Pago',
                            url: appService.ws_recaudacion_orden_pago_reporte_consolidado
                        },
                        {
                            id: 3, nombre: 'Reporte Consolidado de venta por Productos',
                            url: appService.ws_recaudacion_orden_pago_reporte_productos
                        },
                        {
                            id: 4, nombre: 'Reporte Consolidado de venta por Código del Producto',
                            url: appService.ws_recaudacion_orden_pago_reporte_productos
                        }
                    ]
                } else {
                    this.listaTipoReporte = []
                    this.dialogService.notificacion('INFORMACIÓN!', 'No existe Puntos de Emisión en estado ACTIVO a mostrar')
                }
            } else {
                this.puntosEmision = []
                this.listaTipoReporte = []
                this.dialogService.notificacion('ERROR!', res.message)
            }
        })

    }

    /**
     * @desc Función que busca los productos de acuerdo al filtro
     * ingresado, relacionado al componente autocomplete
     */
    filtrarProductos(filtro) {
        if (filtro && typeof filtro === "string") {
            let globalSearchPipe = new BuscarPipe();
            return globalSearchPipe.transform(this.productos, filtro);
        } else {
            return this.productos
        }
    }

    /**
     * @desc Función que especifica el campo a ser mostrado si estamos
     * manejando objetos en el autocomplete, para buscar producto
     */
    displayProducto(value) {
        return value && typeof value === 'object' ? value.descripcion : value;
    }

    /**
     * @desc Función que obtiene la lista de productos, si el
     * reporte es de tipo consolidado por codigo del producto
     */
    seleccionTipoReporte($event) {
        if (this.tipoReporte.id == 4) {
            this.productoService.getProductos(window.localStorage.getItem('auth_key')).subscribe(resp => {
                if (resp.status == 200) {
                    this.productos = resp.data;
                    this.productosBuscados = this.filtrarProductos(null)
                }
            })
        }
    }

    /**
     * @desc Función que imprimir el reporte
     */
    generarReporte() {
        console.log()

        if (this.puntoEmision && this.tipoReporte && moment(this.fechaDesde).isValid() && moment(this.fechaHasta).isValid()) {

            let nombreArchivo = "";
            let token = localStorage.getItem(ComunEnum.AUTH_KEY);
            let data = {
                fechaDesde: moment(this.fechaDesde).format('YYYY-MM-DD'),
                fechaHasta: moment(this.fechaHasta).format('YYYY-MM-DD'),
                puntoEmision: this.puntoEmision.id,
                formato: this.tipoFormato,
                tipo: 'admin'
            };

            if (this.tipoReporte.id == 1 || this.tipoReporte.id == 2) {
                nombreArchivo = this.tipoReporte.id == 1 ? 'consolidado-facturas-generadas.xlsx' : 'consolidado-ordenes-pago.xlsx';

            } else if (this.tipoReporte.id == 3) {
                nombreArchivo = 'consolidado-venta-productos.xlsx';

            } else if (this.tipoReporte.id == 4 && typeof this.producto === 'object') {
                data['producto'] = this.producto.id;
                nombreArchivo = 'consolidado-venta-producto.xlsx';
            } else {
                this.dialogService.notificacion('ERROR!', 'El campo producto es obligatorio para el tipo de reporte seleccionado');
                return;
            }

            if (this.tipoFormato == 'pdf') {
                this.resourceService.printObjetoBlobPorPost(this.tipoReporte.url, data, token, this.homeComponent);
            } else {
                this.resourceService.printObjetoBlobPorPostByNameFile(this.tipoReporte.url, data, token, nombreArchivo, this.homeComponent);
            }

        }
    }
}
