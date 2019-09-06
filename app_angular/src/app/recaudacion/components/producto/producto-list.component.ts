import {Component, OnInit, ViewContainerRef} from "@angular/core";
import {Router, ActivatedRoute} from "@angular/router";
import {ProductoService} from "../../services/producto.service";
import {DialogService} from "../../../shared/comun/services/dialog.service";
import {UtilService} from "../../../shared/comun/services/util.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {Producto} from "../../models/producto.model";
import {DetalleParametrizacionEnum, ComunEnum} from "../../../shared/comun/utils/enums";
import {appService} from "../../../credentials";


@Component({
    moduleId: module.id,
    selector: 'recuadacion-producto-list',
    templateUrl: './producto-list.component.html'
})

export class ProductoListComponent implements OnInit {

    displayedColumns: string[] = ['action', 'codigo', 'descripcion', 'valor', 'facturable', 'tipo_factura', 'activo', 'editable'];
    activarEditar: boolean;
    activarEliminar: boolean;
    activarBuscador: boolean;
    productos: Producto [] = [];
    productosSeleccionados: Producto[];
    filtro: string;
    pagina: number;
    itemsPorPagina: number;
    servicio: string;
    botones = {
        showIniciar: true,
        showCrear: true,
        showEditar: true,
        showEliminar: true,
        showBuscador: true
    }

    constructor(private productoService: ProductoService,
                private resourceService: ResourceService,
                private utilService: UtilService,
                private dialogService: DialogService,
                private router: Router,
                private route: ActivatedRoute,
                private viewContainerRef: ViewContainerRef) {
    }

    /**
     * @desc Función inicializadora del componente
     */
    ngOnInit() {
        this.activarEditar = false;
        this.activarEliminar = false;
        this.activarBuscador = false;
        this.productosSeleccionados = [];
        this.filtro = '';
        this.pagina = 1;
        this.itemsPorPagina = Number(localStorage.getItem(DetalleParametrizacionEnum.ROWS_TABLE))
        this.servicio = appService.ws_recaudacion_productos_paginacion;
    }

    /**
     * @desc Función que inicializa las variables y las lista de productos. El obtener
     * la lista de items solo se requiere cuando deseamos que el boton ACTUALIZAR cargue
     * nuevamente con los valores por defecto
     */
    initProductos() {
        this.ngOnInit();
        this.resourceService.getObjectsPagination(
            this.servicio, localStorage.getItem(ComunEnum.AUTH_KEY),
            this.pagina, this.itemsPorPagina, this.filtro)
            .subscribe(res => {
                if (res.status == 200) {
                    this.productos = res.data;
                }
            });
    }

    /**
     * @desc Función que almacena los items seleccionados para proceder
     * a ejecutar las operaciones definidas (delete, edit)
     * @param {Producto} item - Producto a insertar o eliminar de la lista de seleccionados
     */
    selectedItem(item: Producto) {
        var idx = this.productosSeleccionados.indexOf(item);
        if (idx > -1) {
            this.productosSeleccionados.splice(idx, 1);
        } else {
            this.productosSeleccionados.push(item);
        }
        this.changeBotones(this.productosSeleccionados.length)
    }

    /**
     * @desc Función que verifica si el item esta o no seleccionada
     */
    esItemSeleccionado(item) {
        return this.utilService.existeItemPorId(item, this.productosSeleccionados);
    }

    /**
     * @desc Función que llama al componente que permite
     * crear un item, producto-detail.component
     */
    crear() {
        let link = ['../recaudacion-producto-detail', 0];
        this.router.navigate(link, {relativeTo: this.route});
    }

    /**
     * @desc Función que llama al componente que permite
     * editar un item, producto-detail.component
     */
    editar() {
        let link = ['../recaudacion-producto-detail', this.productosSeleccionados[0].id];
        this.router.navigate(link, {relativeTo: this.route});
    }

    /**
     * @desc Función para confirmar si desea eliminar
     * uno O varios Productos
     */
    confirmarEliminarProducto() {
        this.dialogService.confirm('ELIMINACIÓN DE PRODUCTO(S)', '¿Seguro desea eliminar el/los Producto(s) seleccionadas ?', this.viewContainerRef)
            .subscribe(res => {
                if (res == true) {
                    this.eliminar()
                }
            });
    }

    /**
     * @desc Función que elimina uno o varios
     * productos
     */
    eliminar() {
        let deleteExit = 0;
        let deleteError = 0;
        let msg = "";
        for (let item in this.productosSeleccionados) {
            this.productoService.deleteProducto(window.localStorage.getItem('auth_key'), this.productosSeleccionados[item].id)
                .subscribe(res => {
                    msg += res.message + '\n';
                    res.status == 200 ? deleteExit += 1 : deleteError += 1;
                    if ((deleteExit + deleteError) == this.productosSeleccionados.length) {
                        this.dialogService.notificacion('ELIMINACIÓN DE PRODUCTO(S)', msg, this.viewContainerRef)
                            .subscribe(() => {
                                this.initProductos();
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
