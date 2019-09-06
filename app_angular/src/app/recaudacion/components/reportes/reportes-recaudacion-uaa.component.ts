import {Component, OnInit} from '@angular/core';
import {PuntoEmisionService} from '../../services/punto-emision.service';
import {DialogService} from "../../../shared/comun/services/dialog.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {ProductoService} from "../../services/producto.service";
import {PuntoEmision} from "../../models/punto-emison.model";
import {appService} from "../../../credentials";
import {ComunEnum} from "../../../shared/comun/utils/enums";
import * as moment from "moment";
import {Producto} from "../../models/producto.model";
import {BuscarPipe} from "../../../shared/comun/pipes/buscar/buscar.pipe";
import {HomeComponent} from "../../../home/home.component";

@Component({
    moduleId: module.id,
    selector: 'reportes-recaudacion-uaa',
    templateUrl: 'reportes-recaudacion.component.html'
})

export class ReportesRecaudacionUaaComponent implements OnInit {

    fechaDesde: Date;
    productos: Producto[];
    productosBuscados: Producto[];
    fechaHasta: Date;
    puntoEmision: PuntoEmision;
    puntosEmision: PuntoEmision[];
    tipoReporte: any;
    tipoFormato: string = "pdf"; //pdf|excel
    listaTipoReporte: any = [];
    producto: Producto;
    botones = {showIniciar: true}
    columns = [
        {title: 'Secuencial', dataKey: 'secuencial'},
        {title: 'Fecha', dataKey: 'fecha'},
        {title: 'Cliente', dataKey: 'cliente'},
        {title: 'Rubro', dataKey: 'rubro'},
        {title: 'Cantidad', dataKey: 'cantidad'},
        {title: 'Precio Unit', dataKey: 'precioUnit'},
        {title: 'Subtotal', dataKey: 'subtotal'},
        {title: 'Impuesto', dataKey: 'impuesto'},
        {title: 'Valor Imp.', dataKey: 'valorImp'},
        {title: 'Total', dataKey: 'total'},
    ];
    dataPDF: any;

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
        this.fechaDesde = new Date()
        this.fechaHasta = new Date()
        this.puntoEmision = undefined;
        this.tipoReporte = undefined;
        this.puntosemisionService.getPuntosEmisionInFuncionario(window.localStorage.getItem('auth_key')).subscribe(res => {
            if (res.status == 200) {
                this.puntosEmision = res.data
                this.listaTipoReporte = [
                    {
                        id: 1,
                        nombre: 'Reporte Consolidado de las Ordenes de Pago del Funcionario',
                        url: appService.ws_recaudacion_orden_pago_reporte_consolidado
                    },
                    {
                        id: 2,
                        nombre: 'Reporte Consolidado de todas las Ordenes de Pago',
                        url: appService.ws_recaudacion_orden_pago_reporte_consolidado
                    },
                    {
                        id: 3,
                        nombre: 'Reporte Consolidado de venta por Productos',
                        url: appService.ws_recaudacion_orden_pago_reporte_productos
                    },
                    {
                        id: 4,
                        nombre: 'Reporte Consolidado de venta por Código del Producto',
                        url: appService.ws_recaudacion_orden_pago_reporte_productos
                    }
                ]
            } else {
                this.puntosEmision = []
                this.listaTipoReporte = []
                this.dialogService.notificacion('ERROR!', res.message)
            }
        })

    }

    /**
     * @desc Función que imprimir el reporte
     */
    generarReporte() {
        if (this.puntoEmision && this.tipoReporte && moment(this.fechaDesde).isValid() && moment(this.fechaHasta).isValid()) {
            let nombreArchivo = "";
            let token = localStorage.getItem(ComunEnum.AUTH_KEY);
            let data = {
                fechaDesde: moment(this.fechaDesde).format('YYYY-MM-DD'),
                fechaHasta: moment(this.fechaHasta).format('YYYY-MM-DD'),
                puntoEmision: this.puntoEmision.id,
                formato: this.tipoFormato,
                tipo: 'uaa'
            };

            if (this.tipoReporte.id == 1) {
                nombreArchivo = 'consolidado-ordenes-pago.xlsx';

            } else if (this.tipoReporte.id == 2) {
                data['tipo'] = 'admin';
                nombreArchivo = 'consolidado-ordenes-pago-todas.xlsx';

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

}
