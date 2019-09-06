import {Component, Injectable, OnInit, ViewContainerRef} from '@angular/core';
import {ActivatedRoute, Params, Router} from '@angular/router';
import {FormBuilder, Validators} from '@angular/forms';

import {FlatTreeControl} from '@angular/cdk/tree';
import {CollectionViewer, SelectionChange} from '@angular/cdk/collections';
import {BehaviorSubject, merge, Observable} from 'rxjs';
import {map} from 'rxjs/operators';

import {Producto} from '../../models/producto.model';
import {UAA} from '../../../organico/models/uaa.model';
import {ProductoService} from '../../services/producto.service';
import {DetalleParametrizacionService} from '../../../configuracion/services/detalle-parametrizacion.service';
import {ValidacionService} from '../../../shared/comun/services/validacion.service';
import {DialogService} from '../../../shared/comun/services/dialog.service';
import {UAAService} from '../../../organico/services/uaa.services';
import {UtilService} from "../../../shared/comun/services/util.service";


export class DynamicFlatNode {
    constructor(public item: UAA, public level = 1, public expandable = false, public isLoading = false) {
    }
}

@Injectable()
export class DynamicDataSource {

    dataChange = new BehaviorSubject<DynamicFlatNode[]>([]);

    get data(): DynamicFlatNode[] {
        return this.dataChange.value;
    }

    set data(value: DynamicFlatNode[]) {
        this.treeControl.dataNodes = value;
        this.dataChange.next(value);
    }

    constructor(private treeControl: FlatTreeControl<DynamicFlatNode>,
                private uaaService: UAAService) {
    }

    connect(collectionViewer: CollectionViewer): Observable<DynamicFlatNode[]> {
        this.treeControl.expansionModel.onChange.subscribe(change => {
            if ((change as SelectionChange<DynamicFlatNode>).added ||
                (change as SelectionChange<DynamicFlatNode>).removed) {
                this.handleTreeControl(change as SelectionChange<DynamicFlatNode>);
            }
        });

        return merge(collectionViewer.viewChange, this.dataChange).pipe(map(() => this.data));
    }

    /** Handle expand/collapse behaviors */
    handleTreeControl(change: SelectionChange<DynamicFlatNode>) {
        if (change.added) {
            change.added.forEach(node => this.toggleNode(node, true));
        }
        if (change.removed) {
            change.removed.slice().reverse().forEach(node => this.toggleNode(node, false));
        }
    }

    /**
     * Toggle the node, remove from display list
     */
    toggleNode(node: DynamicFlatNode, expand: boolean) {

        const index = this.data.indexOf(node);
        if (index < 0) { // Cannot find the node, no op
            return;
        }

        if (expand) {
            this.uaaService.getUaasChildren(window.localStorage.getItem('auth_key'), node.item.id)
                .subscribe(res => {
                    if (res.status == 200) {
                        //*****************************
                        //Carga los children
                        //*****************************
                        const children = res.data.length ? res.data : undefined;
                        if (!children) { // If no children, no op
                            return;
                        }

                        node.isLoading = true;
                        setTimeout(() => {
                            //*****************************
                            //Si es expandible o no
                            //*****************************
                            const nodes = children.map(item => new DynamicFlatNode(item, node.level + 1, item.es_padre));
                            this.data.splice(index + 1, 0, ...nodes);
                            // notify the change
                            this.dataChange.next(this.data);
                            node.isLoading = false;
                        }, 1000);

                    }
                });
        } else {
            node.isLoading = true;
            setTimeout(() => {
                let count = 0;
                for (let i = index + 1; i < this.data.length && this.data[i].level > node.level; i++, count++) {
                }
                this.data.splice(index + 1, count);
                // notify the change
                this.dataChange.next(this.data);
                node.isLoading = false;
            }, 1000);

        }

    }
}

@Component({
    moduleId: module.id,
    selector: 'recaudacion-producto-detail',
    templateUrl: './producto-detail.component.html'
})

export class ProductoDetailComponent implements OnInit {

    activarAgregar: boolean;
    activarEliminar: boolean;
    listaTipoImpuesto: any;
    listUaaSeleccionados: any[];
    producto: Producto;
    formProducto: any;
    botones = {
        showCrear: true,
        showEliminar: true
    };

    // Tree
    listaUaaAgregar: UAA[] = [];
    treeControl: FlatTreeControl<DynamicFlatNode>;
    dataSource: DynamicDataSource;
    getLevel = (node: DynamicFlatNode) => node.level;
    isExpandable = (node: DynamicFlatNode) => node.expandable;
    hasChild = (_: number, _nodeData: DynamicFlatNode) => _nodeData.expandable;

    constructor(private route: ActivatedRoute,
                private router: Router,
                private productoServicio: ProductoService,
                private detalleParametrizacionService: DetalleParametrizacionService,
                private formBuilder: FormBuilder,
                private dialogService: DialogService,
                private uaaService: UAAService,
                private utilService: UtilService,
                private viewContainerRef: ViewContainerRef) {
        //Tree
        this.treeControl = new FlatTreeControl<DynamicFlatNode>(this.getLevel, this.isExpandable);
        this.dataSource = new DynamicDataSource(this.treeControl, uaaService);
        //*****************************
        //Carga los datos iniciales del tree
        //*****************************
        this.initialDataSource();
    }

    /**
     * @desc Función que carga los datos del componente Tree
     */
    initialDataSource() {
        let dynamicFlatNode: DynamicFlatNode[] = [];
        this.uaaService.getUaasFathers(window.localStorage.getItem('auth_key'))
            .subscribe(res => {
                if (res.status == 200) {
                    dynamicFlatNode = res.data.map(item => new DynamicFlatNode(item, 0, item.es_padre));
                    this.dataSource.data = dynamicFlatNode;
                }
            });
    }

    /**
     * @desc Función inicializadora
     * del componente
     */
    ngOnInit() {
        this.initVariables()
        this.route.params.forEach((params: Params) => {
            let id = +params['id'];
            id === 0 ? this.newItem() : this.loadItem(id);
        });
    }

    /**
     * @desc Función inicializadora
     * del variables
     */
    initVariables() {
        this.activarAgregar = false;
        this.activarEliminar = false;
        this.listUaaSeleccionados = [];
        this.formProducto = this.formBuilder.group({
            'codigo': ['', Validators.required],
            'descripcion': ['', Validators.required],
            'valor': ['0', [Validators.required, ValidacionService.validadorEsNumeroODecimal]],
            'tipo_impuesto': ['', Validators.required],
            'tipo_unidad': ['', Validators.required],
            'facturable': '',
            'activo': '',
            'editable': ''
        });
        this.detalleParametrizacionService.getDetallesParametrizacionPorParametrizacion(window.localStorage.getItem('auth_key'), 'TIPO_IMPUESTO')
            .subscribe(resp => {
                this.listaTipoImpuesto = resp.data
            });
    }

    /**
     * @desc Función que recupera los datos asociados a
     * un producto e inicializa variables.
     * @param {Number} id - Itendificador del Producto
     */
    loadItem(id) {
        this.productoServicio.getProducto(window.localStorage.getItem('auth_key'), id)
            .subscribe(resp => {
                if (resp.status == 200) {
                    this.producto = <Producto>resp.data;
                    this.producto.tipo_factura = resp.data.tipo_factura ? this.producto.tipo_factura.id : resp.data.tipo_factura;
                    this.producto.tipo_unidad = resp.data.tipo_unidad ? this.producto.tipo_unidad.id : resp.data.tipo_unidad;
                    this.producto.tipo_impuesto = resp.data.tipo_impuesto ? this.producto.tipo_impuesto.id : resp.data.tipo_unidad;
                    this.formProducto.controls['tipo_unidad'].setValue(this.producto.tipo_unidad);
                }
            });
    }

    /**
     * @desc Función que crea un nuevo producto
     * e inicializa variables por defecto
     */
    newItem() {
        this.producto = new Producto();
    }

    /**
     * @desc Función que guarda o actualiza los
     * datos asociados al producto
     */
    guardar() {
        if (this.producto.tipo_unidad && this.producto.tipo_impuesto && ((this.producto.facturable && this.producto.tipo_factura) || !this.producto.facturable)) {
            this.productoServicio.guardarProducto(window.localStorage.getItem('auth_key'), this.producto)
                .subscribe(resp => {
                    if (resp.status == 200) {
                        this.dialogService.notificacion('ÉXITO!', 'El producto ha sido guardado con éxito', this.viewContainerRef)
                            .subscribe(() => {
                                this.navigate(['home/recaudacion-producto-detail', resp.data.id])
                            });
                    } else {
                        let msg = this.mensaje(resp.message);
                        this.dialogService.notificacion('ERROR!', msg, this.viewContainerRef)
                    }
                })
        }
    }

    /**
     * @desc Función que forma cadena de texto a partir de un array.
     * Array contiene los errores del serializer del API
     */
    mensaje(mensaje) {
        let msg = '';
        for (var propiedad in mensaje) {
            msg += propiedad.toLocaleUpperCase() + '\t'
            for (let txt of mensaje[propiedad]) {
                msg += txt
            }
            msg += '\n'
        }
        return msg;
    }

    /**
     * @desc Función agrega una Unidad Academica
     * Administrativa (UAA) al producto
     */
    agregarUaa() {
        let asigar = {
            'ids_uaa': this.listaUaaAgregar.map(item => item.id),
            'id_producto': this.producto.id
        }

        this.productoServicio.asignarUaasInProducto(window.localStorage.getItem('auth_key'), asigar)
            .subscribe(resp => {
                if (resp.status == 200) {
                    this.dialogService.notificacion('ÉXITO!', 'Las Unidades Académicas Administrativas han sido asignadas al ṕroducto', this.viewContainerRef)
                        .subscribe(() => {
                            this.loadItem(this.producto.id)
                            this.changeAgregar()
                        });
                }
            })
    }

    /**
     * @desc Función para confirmar si desea eliminar una Unidad
     * Academica Administrativa (UAA) al producto
     */
    confirmarEliminarUaa() {
        this.dialogService.confirm('Unidad Académica Administrativa (UAA)', '¿Seguro desea eliminar la(s) UAA(S) seleccionada(s) del producto?', this.viewContainerRef)
            .subscribe(res => {
                if (res == true) {
                    this.eliminarUaa()
                }
            });
    }

    /**
     * @desc Función que elimina una Unidad Academica
     * Administrativa (UAA) al producto
     */
    eliminarUaa() {
        let deleteExit = 0
        let deleteError = 0
        let msg = ''
        for (let i in this.listUaaSeleccionados) {
            let objeto = {
                'id_uaa': this.listUaaSeleccionados[i].id,
                'id_producto': this.producto.id
            }
            this.productoServicio.deleteUaaInProducto(window.localStorage.getItem('auth_key'), objeto)
                .subscribe(res => {
                    res.status == 200 ? deleteExit += 1 : deleteError += 1
                    if ((deleteExit + deleteError) == this.listUaaSeleccionados.length) {
                        msg = deleteExit != 0 ? 'Se ha eliminado con éxito ' + deleteExit + ' elemento(s)\n' : ''
                        msg += deleteError != 0 ? 'No se pueden eliminar ' + deleteExit + ' elemento(s)' : ''
                        this.dialogService.notificacion('ELIMINACIÓN DE UAA(S)', msg, this.viewContainerRef)
                            .subscribe(() => {
                                this.loadItem(this.producto.id)
                                this.listUaaSeleccionados = []
                                this.changeEliminar()
                            });
                    }
                })
        }
    }

    /**
     * @desc Función que actualiza la variable tipo de unidad y el estado de los
     * campos que son subcomponentes y se ajuste a los valiadores de los formularios
     */
    changeTipoUnidad(value) {
        this.producto.tipo_unidad = value;
        this.formProducto.controls['tipo_unidad'].setValue(value);
        this.formProducto.controls['tipo_unidad'].markAsTouched();
    }

    /**
     * @desc Función que habilita o desabilita el campo
     * tipo de factura de acuerdo al estado de facturable
     * de objeto producto
     */
    changeFacturable() {
        if (this.producto.facturable == false) {
            this.producto.tipo_factura = undefined;
        }
    }

    /**
     * @desc Función que actualiza el estado
     * de la variable que habilita la opcion
     * de agregar UAA
     */
    changeAgregar() {
        this.activarAgregar ? this.activarAgregar = false : this.activarAgregar = true;
        if (this.activarAgregar) {
            this.listaUaaAgregar = []
        }
    }

    /**
     * @desc Función que actualiza el estado
     * de la variable para habilitar la eliminación
     * de UAA
     */
    changeEliminar() {
        this.listUaaSeleccionados.length == 0 ? this.activarEliminar = false : this.activarEliminar = true
    }

    /**
     * @desc Función que navega al componente
     * que recibe como parametro
     */
    navigate(link = null) {
        link ? this.router.navigate(link) : this.router.navigate(['home/recaudacion-producto-list']);
    }

    /**
     * @desc Función que almacena los items seleccionados
     * @param item - item a insertar o eliminar de la lista de seleccionados
     */
    selectedItem(item) {
        var idx = this.listaUaaAgregar.indexOf(item);
        if (idx > -1) {
            this.listaUaaAgregar.splice(idx, 1);
        } else {
            this.listaUaaAgregar.push(item);
        }
    }

    /**
     * @desc Función que verifica si el item esta o no seleccionada
     */
    esItemSeleccionado(item) {
        return this.utilService.existeItemPorId(item, this.listaUaaAgregar);
    }


}
