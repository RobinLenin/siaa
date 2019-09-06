import {Component, OnInit, ViewContainerRef} from "@angular/core";
import {ActivatedRoute, Params, Router} from "@angular/router";
import {FormBuilder, Validators} from "@angular/forms";
import {MatDialog, MatSnackBar} from "@angular/material";

import {DialogService} from "../../../shared/comun/services/dialog.service";
import {DetalleParametrizacionService} from "../../../configuracion/services/detalle-parametrizacion.service";
import {OrdenPagoService} from "../../services/orden-pago.service";
import {ProductoService} from "../../services/producto.service";
import {PersonaService} from "../../../core/services/persona.service";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {ValidacionService} from "../../../shared/comun/services/validacion.service";

import {Direccion} from "../../../core/models/direccion.model";
import {OrdenPago} from "../../models/orden-pago.model";
import {OrdenPagoDetalle} from "../../models/orden-pago-detalle.model";
import {Persona} from "../../../core/models/persona.model";
import {Producto} from "../../models/producto.model";
import {PuntoEmisionUAA} from "../../models/punto-emision-uaa.model";

import {BuscarPipe} from '../../../shared/comun/pipes/buscar/buscar.pipe';
import {ModalPagoComponent} from "./modal-pago.component";
import {appService} from "../../../credentials";
import {ComunEnum} from "../../../shared/comun/utils/enums";


@Component({
    moduleId: module.id,
    selector: 'recaudacion-orden-pago-detail',
    templateUrl: './orden-pago-detail.component.html'
})

export class OrdenPagoDetailComponent implements OnInit {

    myStyles = {'width': '50%'};
    masAcciones = [{nombre: 'Ver en Pdf', codigo: 'ver_pdf', icon: 'print', desabilitar: true}];
    editando: boolean;
    activarAgregar: boolean;
    activarEliImp: boolean;
    activarEditar: boolean;
    activarEdicion: boolean;
    activarAccion: boolean;
    showOrdenPago: boolean;
    desglosarDetalle: boolean;
    selecTodos: boolean = false;
    consumidorFinal = '9999999999999';
    consumidorFinalBase = 199;
    numero_documento: string;
    msgOrdenPago: string;
    puntoEmisionUaa: PuntoEmisionUAA;
    ordenPago: OrdenPago;
    ordenPagoDetalle: OrdenPagoDetalle;
    ordenPagoDetalleSelec: OrdenPagoDetalle[];
    ordenPagoDetalleSubtotales = [];
    ordenPagoDetalleImpuestos = [];
    productos: Producto[] = [];
    productosBuscados: Producto[] = [];
    formOrdenPagoDetalle: any;
    botones: any;

    constructor(public dialog: MatDialog,
                private route: ActivatedRoute,
                private router: Router,
                private ordenPagoService: OrdenPagoService,
                private productoService: ProductoService,
                private personaService: PersonaService,
                private formBuilder: FormBuilder,
                private dialogService: DialogService,
                private viewContainerRef: ViewContainerRef,
                private snackBar: MatSnackBar,
                private resourceService: ResourceService,
                private detalleParametrizacionService: DetalleParametrizacionService) {

    }


    /**
     * @desc Función inicializadora
     * del componente
     */
    ngOnInit() {
        this.route.params.forEach((params: Params) => {
            let id = +params['id'];
            this.loadItem(id)
        });
    }

    /**
     * @desc Función inicializadora del
     * variables
     */
    initVariables() {
        this.ordenPagoDetalleSelec = []
        this.editando = false
        this.activarAgregar = false
        this.activarEliImp = false
        this.activarEditar = false
        if (this.ordenPago.id) {
            this.activarEdicion = false
            this.botones = {
                showImprimirBlob: true,
                showMasAcciones: true
            }
        } else {
            this.activarEdicion = true
            this.botones = {
                showCrear: true,
                showEditar: true,
                showEliminar: true
            }
        }
        this.changeAccion()
        this.getSubtotalesAll()
    }

    /**
     * @desc Función que recupera los datos asociados a
     * la Orden de Pago e inicializa variables. Los datos a
     * recuperar es la Orden de Pago y sus Ordenes de Pago Detalle.
     * @param {Number} id - Itendificador de la Orden de Pago
     */
    loadItem(id) {
        if (localStorage.getItem("puntoEmisionUaa")) {
            this.puntoEmisionUaa = JSON.parse(localStorage.getItem("puntoEmisionUaa"));
            this.ordenPagoService.getOrdenPago(window.localStorage.getItem('auth_key'), id, this.puntoEmisionUaa.id)
                .subscribe(resp => {
                    if (resp.status == 200) {
                        this.ordenPago = <OrdenPago>resp.data
                        this.ordenPago.id ? this.showOrdenPago = true : this.showOrdenPago = false
                        this.initVariables()
                    } else {
                        this.dialogService.notificacion('ERROR!', resp.message, this.viewContainerRef)
                    }
                });
        } else {
            this.dialogService.notificacion('ERROR!', 'No existe un Punto de Emisión UAA seleccionado en la lista de Ordenes de Pago', this.viewContainerRef)
        }
    }

    /**
     * @desc Función que ejecuta la
     * acción a guardar o anular una orden de pago
     */
    accionOrdenPago(formOrdenPago) {
        if (this.activarEdicion) {
            this.guardarOrdenPago(formOrdenPago);
        } else {
            this.confirmarAnularOrdenPago();
        }
    }

    /**
     * @desc Función que guarda
     * una Orden de Pago
     */
    guardarOrdenPago(formOrdenPago) {
        if (formOrdenPago.valid && this.ordenPago.persona.tipo_documento &&
            this.ordenPago.persona.sexo && this.ordenPago.ordenes_pago_detalle.length > 0) {

            // Valido que si es consumidor final, no sobrepase la base
            if (this.ordenPago.persona.numero_documento == this.consumidorFinal && this.ordenPago.total > this.consumidorFinalBase) {
                this.dialogService.notificacion(
                    'ERROR!',
                    'El total ' +this.ordenPago.total+ ' es mayor al valor base de consumidor final ' + this.consumidorFinalBase,
                    this.viewContainerRef)
            } else {
                let sumTotalItems = this.getTotalAll();
                let sumSubtotalesIva = this.getTotalAllCuadre();

                // Valido que los totales cuadren
                if (sumTotalItems.toFixed(4) == sumSubtotalesIva.toFixed(4)) {
                    const dialogRef = this.dialog.open(ModalPagoComponent, {
                        width: '500px',
                        data: {'ordenPago': this.ordenPago, 'opcion': 'NUEVO'}
                    });
                    dialogRef.afterClosed().subscribe(resp => {
                        if (resp) {
                            this.dialogService.notificacion('ÉXITO!', 'La orden de pago ha sido creada con éxito', this.viewContainerRef)
                                .subscribe(() => {
                                    let link = ['home/recaudacion-orden-pago-detail', resp];
                                    this.router.navigate(link)
                                });
                        }
                    });

                } else {
                    let msg = 'La sumatoria de los totales de cada item individual no es igual a la sumatoria de los subtotales/iva' +
                        '\nSumatoria total item(s): ' + sumTotalItems +
                        '\nSumatoria subtotales/iva: ' + sumSubtotalesIva
                    this.dialogService.notificacion('ERROR!', msg, this.viewContainerRef)
                }
            }
        }
    }

    /**
     * @desc Función para confirmar si desea anular
     * una orden de pago
     */
    confirmarAnularOrdenPago() {
        if (this.ordenPago.estado == 'EMITIDA') {
            this.dialogService.confirm('PROCESO DE ALTO RIESGO!', 'Seguro desea ANULAR la orden de pago con sus items', this.viewContainerRef)
                .subscribe(res => {
                    if (res == true) {
                        this.anularOrdenPago()
                    }
                });
        } else {
            this.snackBar.open("La orden de pago tiene que estar en estado de EMITIDA", 'Aceptar', {duration: 5000});
        }
    }

    /**
     * @desc Función que anula
     * la orden de pago
     */
    anularOrdenPago() {
        this.ordenPagoService.anularOrdenPago(window.localStorage.getItem('auth_key'), this.ordenPago.id)
            .subscribe(resp => {
                if (resp.status == 200) {
                    this.dialogService.notificacion('ÉXITO!', resp.message, this.viewContainerRef)
                        .subscribe(() => {
                            this.loadItem(this.ordenPago.id);
                        });
                } else {
                    this.dialogService.notificacion('ERROR!', resp.message, this.viewContainerRef);
                }
            })
    }

    /**
     * @desc Función que obtiene la lista de los productos
     * que pertenecen a la Unidad Academica Administrativa
     * del funcionario en sesión
     */
    getProductosInFuncionarioInUaa() {
        this.productoService.getProductosInFuncionarioInUaa(window.localStorage.getItem('auth_key'))
            .subscribe(resp => {
                if (resp.status == 200) {
                    this.productos = resp.data
                    this.productosBuscados = this.filtrarProductos(null)
                }
            })
    }

    /**
     * @desc Función que busca los productos de acuerdo al filtro
     * ingresado, relacionado al componente autocomplete
     */
    filtrarProductos(filtro: any) {
        if (filtro && typeof filtro === "string") {
            let globalSearchPipe = new BuscarPipe();
            return globalSearchPipe.transform(this.productos, filtro);
        } else {
            if (this.ordenPagoDetalle.producto) {
                if (this.ordenPagoDetalle.producto.editable) {
                    this.formOrdenPagoDetalle.get('precio').enable();
                    if (!this.activarEditar && !this.editando) {
                        this.ordenPagoDetalle.precio = this.ordenPagoDetalle.producto.valor;
                    }
                } else {
                    this.formOrdenPagoDetalle.get('precio').disable();
                    this.ordenPagoDetalle.precio = this.ordenPagoDetalle.producto.valor;
                }

            }
            return this.productos
        }
    }

    /**
     * @desc Función que especifica el campo a ser mostrado si estamos
     * manejando objetos en el autocomplete
     */
    displayProducto(value: any): string {
        return value && typeof value === 'object' ? value.descripcion : value;
    }

    /**
     * @desc Función que crea una orden de pago
     * detalle para la Orden de Pago en la que
     * se esta actualmente
     */
    crearOrdenPagoDetalleInOrdenPago() {
        if (this.activarEdicion && parseInt(this.ordenPagoDetalle.cantidad) > 0 && this.ordenPagoDetalle.total > 0) {

            this.ordenPagoDetalle.secuencial = 0;
            this.ordenPagoDetalle.tipo_impuesto = this.ordenPagoDetalle.producto.tipo_impuesto;
            this.ordenPagoDetalle.impuesto_tarifa = this.ordenPagoDetalle.producto.tipo_impuesto.valor;
            this.ordenPagoDetalle.impuesto_codigo = this.ordenPagoDetalle.producto.tipo_impuesto.codigo;
            this.ordenPagoDetalle.producto_codigo = this.ordenPagoDetalle.producto.codigo;
            this.ordenPagoDetalle.producto_descripcion = this.ordenPagoDetalle.producto.descripcion;

            if (this.desglosarDetalle) {
                let cant = this.ordenPagoDetalle.cantidad;
                this.ordenPagoDetalle.cantidad = 1;
                this.getPrecioUnitarioProducto(this.ordenPagoDetalle);
                this.getSubTotalProducto(this.ordenPagoDetalle);
                this.getValorImpuestoProducto(this.ordenPagoDetalle);
                this.getTotalProducto(this.ordenPagoDetalle);

                if (this.activarEditar && this.editando) {
                    let pos = this.ordenPago.ordenes_pago_detalle.indexOf(this.ordenPagoDetalleSelec[0]);
                    this.ordenPago.ordenes_pago_detalle[pos] = this.ordenPagoDetalle;
                    cant = cant - 1;
                }

                for (let i = 0; i < cant; i++) {
                    let copy = Object.assign({}, this.ordenPagoDetalle);
                    this.ordenPago.ordenes_pago_detalle.push(copy);
                }

            } else {
                if (this.activarEditar && this.editando) {
                    let pos = this.ordenPago.ordenes_pago_detalle.indexOf(this.ordenPagoDetalleSelec[0]);
                    this.ordenPago.ordenes_pago_detalle[pos] = this.ordenPagoDetalle;
                } else {
                    this.ordenPago.ordenes_pago_detalle.push(this.ordenPagoDetalle);
                }
            }

            if (this.activarEditar && this.editando) {
                this.ordenPagoDetalleSelec = []
                this.changeEliminarImprimir(this.ordenPagoDetalleSelec.length);
            }

            this.cerrarOrdenPagoDetalle();
            this.getSubtotalesAll();
            this.ordenPago.total = this.getTotalAllCuadre()

        } else {
            this.dialogService.notificacion('ERROR!', 'El total correspondiente al item debe ser mayor a 0', this.viewContainerRef);
        }
    }

    /**
     * @desc Función que elimina una o varias
     * ordenes de pago detalle para la Orden de Pago
     * en la que se esta actualmente
     */
    eliminarOrdenPagoDetalleInOrdenPago() {
        if (this.activarEdicion) {
            let deleteExit = 0;
            let deleteError = 0;
            for (let i in this.ordenPagoDetalleSelec) {
                let posicion = this.ordenPago.ordenes_pago_detalle.indexOf(this.ordenPagoDetalleSelec[i])
                let status = this.ordenPago.ordenes_pago_detalle.splice(posicion, 1);
                status ? deleteExit += 1 : deleteError += 1;
                if ((deleteExit + deleteError) == this.ordenPagoDetalleSelec.length) {
                    this.ordenPagoDetalleSelec = [];
                    this.changeEliminarImprimir(this.ordenPagoDetalleSelec.length);
                    this.getSubtotalesAll();
                    this.cerrarOrdenPagoDetalle();
                    this.dialogService.notificacion('ÉXITO!', 'Detalle(s) de Producto(s) eliminado(s)', this.viewContainerRef)
                }
            }
        }
    }

    /**
     * @desc Función que imprime una orden de pago detalle para la Orden de Pago
     * en la que se esta actualmente para la impresora matricial, Se consume un servicio de
     * php (WebClientPrint) que se encarga de obtener los datos del item e imprimir
     */
    imprimirOrdenPagoDetalleWcp() {
        if (!this.activarEdicion) {

            let token = localStorage.getItem(ComunEnum.AUTH_KEY);
            this.detalleParametrizacionService.getDetalleParametrizacionPorCodigo(token, 'URL_IMPRESION_DERECHO_WCP').subscribe(resp => {
                if (resp.status == 200) {

                    //Concatenamos los ids
                    let ids: string = '';
                    for (let i = 0; i < this.ordenPagoDetalleSelec.length; i++) {
                        ids = i == 0 ? this.ordenPagoDetalleSelec[i]['id'].toString() : ids + '-' + this.ordenPagoDetalleSelec[i]['id'];
                    }

                    // Definimos la anchura y altura de la ventana
                    let height = 250;
                    let width = 500;

                    // Calculamos la posicion x e y para centrar la ventana
                    let top = (window.screen.height / 2) - (height / 2);
                    let left = (window.screen.width / 2) - (width / 2);

                    let url = resp.data['valor'] + '?ids=' + ids + "&token=" + token;
                    let win = window.open(url, "Impresión de Derecho", "width=" + width + ", height=" + height + ", top=" + top + ", left=" + left + ", menubar=yes, resizable=no");
                }
            });

        }
    }

    /**
     * @desc Función que ejecuta la acción de acuerdo al menu seleccionado
     * en mas acciones. Imprimir una o varias ordenes de pago detalle en pdf
     */
    ejecutarAccion(accion) {
        if (accion.codigo == 'ver_pdf') {
            if (!this.activarEdicion) {
                let token = localStorage.getItem(ComunEnum.AUTH_KEY);
                this.resourceService.printObjetoBlobPorPost(appService.ws_recaudacion_orden_pago_reporte_detalle, this.ordenPagoDetalleSelec, token)
            }
        }
    }

    /**
     * @desc Función que almacena los items
     * seleccionados para proceder a ejecutar
     * las operaciones definidas
     * @param {OrdenPagoDetalle} item - item a insertar o eliminar de la lista de seleccionados
     */
    selectedItem(item: OrdenPagoDetalle) {
        var idx = this.ordenPagoDetalleSelec.indexOf(item);
        if (idx > -1) {
            this.ordenPagoDetalleSelec.splice(idx, 1);
        } else {
            this.ordenPagoDetalleSelec.push(item);
        }
        this.changeEliminarImprimir(this.ordenPagoDetalleSelec.length)
    }

    /**
     * @desc Función que actualiza la variable
     * que contiene el estado de habilitar/deshabilitar
     * el boton de guardar y anular la orden de pago
     */
    changeAccion() {
        if (this.ordenPago.id) {
            this.msgOrdenPago = 'Anular'
            this.ordenPago.estado == 'ANULADA' ? this.activarAccion = false : this.activarAccion = true
        } else {
            this.activarAccion = true
            this.msgOrdenPago = 'Guardar'
        }
    }

    /**
     * @desc Función que actualiza la variable
     * que contiene el estado para eliminar-imprimir una Orden de
     * Pago Detalle
     */
    changeEliminarImprimir(tamanio) {
        if (tamanio == 0) {
            this.activarEliImp = false;
            this.activarEditar = false;
            this.masAcciones[0].desabilitar = true;
        } else {
            this.activarEditar = tamanio == 1 ? true : false;
            this.activarEliImp = true;
            this.masAcciones[0].desabilitar = false;
        }
    }

    /**
     * @desc Función que actualiza la variable
     * que contiene el estado para agregar una
     * Orden de Pago Detalle
     */
    changeAgregar() {
        this.activarAgregar = true;
        this.editando = false;

        this.ordenPagoDetalle = new OrdenPagoDetalle()
        this.ordenPagoDetalle.producto = ""
        this.desglosarDetalle = false;
        this.getProductosInFuncionarioInUaa();
        this.formOrdenPagoDetalle = this.formBuilder.group({
            'producto': ['', [Validators.required, ValidacionService.validadorAutocompletar]],
            'cantidad': ['', [Validators.required, ValidacionService.validadorEsNumero]],
            'precio': [{value: '', disabled: true}, [Validators.required, ValidacionService.validadorEsNumeroODecimal]],
            'observacion': [''],
            'desglosarDetalle': [this.desglosarDetalle, [Validators.required]]
        });
    }

    /**
     * @desc Función que actualiza las variables para
     * editar una Orden de Pago Detalle
     */
    changeEditar() {
        this.activarAgregar = true;
        this.editando = true;

        this.ordenPagoDetalle = Object.assign({}, this.ordenPagoDetalleSelec[0]);
        this.desglosarDetalle = false;
        this.formOrdenPagoDetalle = this.formBuilder.group({
            'producto': [{
                value: this.ordenPagoDetalle.producto,
                disabled: true
            }, [Validators.required, ValidacionService.validadorAutocompletar]],
            'cantidad': [this.ordenPagoDetalle.cantidad, [Validators.required, ValidacionService.validadorEsNumero]],
            'precio': [{
                value: this.ordenPagoDetalle.precio,
                disabled: true
            }, [Validators.required, ValidacionService.validadorEsNumeroODecimal]],
            'observacion': [this.ordenPagoDetalle.observacion],
            'desglosarDetalle': [this.desglosarDetalle, [Validators.required]]
        });
    }

    /**
     * @desc Cierra la pantalla para crear una orden de Pago detalle
     */
    cerrarOrdenPagoDetalle() {
        this.editando = false;
        this.activarAgregar = false;
        this.ordenPagoDetalle = null;
    }


    /**
     * @desc Función que calcula el precio unitario, el impuesto
     * y el total del producto
     * @param {OrdenPagoDetalle} item - objeto que una orden de pago detalle
     * @returns {Number}-Precio Unitario de la orden de pago detalle a pagar
     */
    getPrecioUnitarioProducto(item) {
        if (item.producto && typeof item.producto === 'object' && item.cantidad && item.precio) {
            let impuesto = item.precio * item.producto.tipo_impuesto.valor
            let impuesto_total = impuesto * item.cantidad;
            item.impuesto = parseFloat(impuesto_total.toFixed(2));
            item.total = (item.cantidad * item.precio) + item.impuesto;

        } else {
            item.impuesto = 0
            item.total = 0
        }
        return item.precio
    }

    /**
     * @desc Función que calcula el sub total por cada
     * orden de pago detalle agregar
     * @param {OrdenPagoDetalle} item - objeto que una orden de pago detalle
     * @returns {Number}-Sub total de la orden de pago detalle a pagar
     */
    getSubTotalProducto(item) {
        let subtotal = 0
        if (item.producto && typeof item.producto === 'object' && item.cantidad && item.precio) {
            subtotal = parseFloat(item.cantidad) * parseFloat(item.precio)
        }
        return subtotal.toFixed(4)
    }

    /**
     * @desc Función que obtiene el tipó de Impuesto por cada
     * orden de pago detalle
     * @param {OrdenPagoDetalle} item - objeto que una orden de pago detalle
     * @returns {Number}-Tipo de iva de la orden de pago detalle
     */
    getTipoImpuestoProducto(item) {
        let tipoIva = item.producto && typeof item.producto === 'object' ? item.producto.tipo_impuesto.nombre : null
        return tipoIva
    }

    /**
     * @desc Función que calcula el impuesto de cada
     * orden de pago detalle agregar
     * @param {OrdenPagoDetalle} item - objeto que una orden de pago detalle
     * @returns {Number}-iva de la orden de pago detalle a pagar
     */
    getValorImpuestoProducto(item) {
        item.impuesto = item.impuesto.toFixed(4)
        return item.impuesto
    }

    /**
     * @desc Función que calcula el valor total a pagar por cada
     * orden de pago detalle agregar
     * @param {OrdenPagoDetalle} item - objeto que una orden de pago detalle
     * @returns {Number}-total de la orden de pago detalle a pagar
     */
    getTotalProducto(item) {
        item.total = item.total.toFixed(2)
        return item.total
    }


    /**
     * @desc Función que calcula el valor total a
     * pagar de la orden de pago
     */
    getSubtotalesAll() {
        this.ordenPagoDetalleSubtotales = this.getTipoSubTotalesAll()
        this.ordenPagoDetalleImpuestos = this.getTipoImpuestosAll()
    }

    /**
     * @desc Función que calcula los tipos subtotales a
     * pagar de la orden de pago
     */
    getTipoSubTotalesAll() {
        let subtotales = []
        for (let i in this.ordenPago.ordenes_pago_detalle) {
            let item = this.ordenPago.ordenes_pago_detalle[i]
            let tipoImpuesto = this.ordenPago.ordenes_pago_detalle[i].producto.tipo_impuesto
            let index = this.buscarItem(subtotales, tipoImpuesto.id)
            if (index) {
                subtotales[index]['subtotal'] += parseFloat(item['cantidad']) * parseFloat(item['precio'])
            } else {
                tipoImpuesto['subtotal'] = parseFloat(item['cantidad']) * parseFloat(item['precio'])
                subtotales.push(tipoImpuesto)
            }
        }
        return subtotales
    }

    /**
     * @desc Función que calcula los valores totales de
     * impuestos a pagar de la orden de pago
     */
    getTipoImpuestosAll() {
        let subtotalesIva = []
        for (let i in this.ordenPago.ordenes_pago_detalle) {
            let item = this.ordenPago.ordenes_pago_detalle[i]
            let tipo_impuesto = this.ordenPago.ordenes_pago_detalle[i].producto.tipo_impuesto
            let index = this.buscarItem(subtotalesIva, tipo_impuesto.id)
            if (index) {
                subtotalesIva[index]['impuesto'] += parseFloat(item['impuesto'])
            } else {
                tipo_impuesto['impuesto'] = parseFloat(item['impuesto'])
                subtotalesIva.push(tipo_impuesto)
            }
        }
        return subtotalesIva
    }

    /**
     * @desc Función que calcula el valor total a
     * pagar de la orden de pago, de acuerdo al total
     * de cada item
     */
    getTotalAll() {
        let total: number = 0
        for (let i in this.ordenPago.ordenes_pago_detalle) {
            total = total + parseFloat(this.ordenPago.ordenes_pago_detalle[i]['total'])
        }
        return total
    }

    /**
     * @desc Función que calcula el valor total a
     * pagar de la orden de pago, de acuerdo a la
     * sumatoria de los subtotoles de toda la orden
     * de pago
     */
    getTotalAllCuadre() {
        let total: number = 0
        for (let i in this.ordenPagoDetalleSubtotales) {
            total = total + parseFloat(this.ordenPagoDetalleSubtotales[i]['subtotal'])
        }
        for (let i in this.ordenPagoDetalleImpuestos) {
            total = total + parseFloat(this.ordenPagoDetalleImpuestos[i]['impuesto'])
        }
        return total
    }

    /**
     * @desc Función muestra el total de la Orden de Pago
     * redondeado a 2 decimales
     */
    getTotalAllCuadreShow() {
        if (this.ordenPago.total) {
            return this.ordenPago.total
        } else {
            let total = this.getTotalAllCuadre();
            return total.toFixed(2);
        }
    }

    /**
     * @desc Función util para identificar un objeto
     * dentro de una lista.
     * @param {Array} lista - lista para buscar un item
     * @param {Number} id - item a buscar en la lista
     * @return {Objeto} - identificador del item encontrado en la lista
     */
    buscarItem(lista, id) {
        for (let i in lista) {
            if (id == lista[i].id) {
                return i
            }
        }
        return null
    }

    /**
     * @desc Función que navega al componente
     * que lo invoca, el cual es listar ordenes
     * de pago
     */
    regresar() {
        this.router.navigate(['home/recaudacion-orden-pago-list'])
    }


    /**
     * @desc Función que recupera los datos personales
     * del cliente para emitir la orden de pago. Utiliza el
     * subcomponente list-persona y se invoca cuando se selecciona un item
     * @param {Persona} persona - Objeto persona que selecciona el usuario
     */
    onChangePersona(val) {
        let personaBuscada = val[0];
        personaBuscada['tipo_documento'] = personaBuscada['tipo_documento']['id'];
        personaBuscada['sexo'] = personaBuscada['sexo']['id'];
        this.asignarPersonaOrdenPago(personaBuscada);
    }

    /**
     * @desc Función que recupera los datos personales
     * del cliente para emitir la orden de pago. Utiliza el
     * subcomponente list-persona y se invoca cuando se presiona enter
     * @param {String} numero_documento - identificación de la persona a buscar
     */
    enterInputPersona(numero_documento) {
        this.personaService.getPersonaOrRegistrocivil(window.localStorage.getItem('auth_key'), numero_documento)
            .subscribe(res => {
                if (res.status == 200) {
                    //Existe la persona en el siaaf o en el registro civil
                    if (res.data) {
                        let personaBuscada = res.data;
                        personaBuscada['tipo_documento'] = personaBuscada['tipo_documento']['id'];
                        personaBuscada['sexo'] = personaBuscada['sexo']['id'];
                        this.asignarPersonaOrdenPago(personaBuscada);
                        //No existe la persona
                    } else {
                        let persona = new Persona();
                        persona.numero_documento = numero_documento;
                        this.asignarPersonaOrdenPago(persona);
                        this.snackBar.open('La persona no se encuentra en el Registro civil, proceda a ingresar los datos', 'Aceptar', {duration: 5000});
                    }
                } else {
                    let persona = new Persona();
                    persona.numero_documento = numero_documento;
                    this.asignarPersonaOrdenPago(persona);
                    this.snackBar.open('Error al consultar del registro civil, proceda a ingresar los datos', 'Aceptar', {duration: 5000});
                }
            });
    }

    /**
     * @desc Asigna la persona a la orden de pago
     * @param persona
     */
    asignarPersonaOrdenPago(persona) {
        this.ordenPago.persona = persona;
        this.ordenPago.ordenes_pago_detalle = [];
        this.initVariables();

        //Existe la persona en el Siaaf
        if ('id' in persona && persona.id != null) {
            this.personaService.getDireccionesPorPersona(window.localStorage.getItem('auth_key'), persona.id)
                .subscribe(resp => {
                    if (resp.status == 200) {
                        let direccion_domicio = resp.data.find(x => (x.tipo_direccion && x.tipo_direccion['nombre'] == "Domicilio"));
                        this.ordenPago.direccion = direccion_domicio ? direccion_domicio : new Direccion();
                        this.showOrdenPago = true;
                    }
                });
        } else {
            this.ordenPago.direccion = new Direccion();
            //Existe la persona en el registro civil
            if ('id' in persona) {
                this.ordenPago.direccion.calle_principal = persona['Calle']
                this.ordenPago.direccion.numero = persona['NumeroCasa']
            }
            this.showOrdenPago = true;
        }
    }

    /**
     * @desc Selecciona o deselecciona las ordenes de pago detalle
     */
    selectedItemAll() {
        this.ordenPagoDetalleSelec = [];
        if (this.selecTodos) {
            for (let i in this.ordenPago.ordenes_pago_detalle) {
                this.selectedItem(this.ordenPago.ordenes_pago_detalle[i]);
            }
        } else {
            this.changeEliminarImprimir(this.ordenPagoDetalleSelec.length)
        }
    }

    /**
     * @desc Verifica si esta seleccionado una orden de pago detalle
     */
    esItemSeleccionado(item) {
        return this.ordenPagoDetalleSelec.indexOf(item) > -1;
    }

}
