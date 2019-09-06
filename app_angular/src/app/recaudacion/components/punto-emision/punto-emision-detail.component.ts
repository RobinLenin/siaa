import {ActivatedRoute, Params, Router} from "@angular/router";
import {Component, OnInit, ViewContainerRef} from "@angular/core";
import {FormBuilder, Validators} from "@angular/forms";
import {DialogService} from "../../../shared/comun/services/dialog.service";
import {FuncionarioService} from "../../../talento-humano/services/funcionario.service";
import {PuntoEmisionService} from "../../services/punto-emision.service";
import {ValidacionService} from "../../../shared/comun/services/validacion.service";
import {PuntoEmision} from "../../models/punto-emison.model";
import {PuntoEmisionUAA} from "../../models/punto-emision-uaa.model";
import {HomeComponent} from "../../../home/home.component";

@Component({
    moduleId: module.id,
    selector: 'recaudacion-punto-emision-detail',
    templateUrl: './punto-emision-detail.component.html'
})

export class PuntoEmisionDetailComponent implements OnInit {

    displayedColumns: string[] = ['action', 'code', 'func', 'description', 'secuencial', 'impresora'];
    private activarAgregar: boolean;
    private activarEliminar: boolean;
    private activarEditar: boolean;
    private listFun: any;
    private listFunSeleccionados: any[];
    public punto_emision: PuntoEmision;
    private punto_emision_uaa: PuntoEmisionUAA[];
    private punto_emision_uaa_new: PuntoEmisionUAA;
    private formPuntoEmision: any;
    private formPuntoEmisionUaa: any;
    botones = {
        showCrear: true,
        showEliminar: true,
        showEditar: true
    };

    constructor(private route: ActivatedRoute,
                private router: Router,
                private puntoEmisionServicio: PuntoEmisionService,
                private funcionarioService: FuncionarioService,
                private formBuilder: FormBuilder,
                private dialogService: DialogService,
                private homeComponent: HomeComponent,
                private viewContainerRef: ViewContainerRef) {
        this.formPuntoEmision = this.formBuilder.group({
            'activo': '',
            'codigo_establecimiento': ['', [Validators.required, Validators.pattern('^[0-9]{3}$')]],
            'codigo_facturero': ['', [Validators.required, Validators.pattern('^[0-9]{3}$')]],
            'descripcion': ['', Validators.required],
            'fechas': this.formBuilder.group({
                'nro_desde': ['', [Validators.required, Validators.pattern('^[0-9]{6}$')]],
                'nro_hasta': ['', [Validators.required, Validators.pattern('^[0-9]{6}$')]]
            }, {validator: ValidacionService.validadorCantidadDesdeMenorHasta})
        });
    }

    /**
     * @desc Función inicializadora
     * del componente
     */
    ngOnInit() {
        this.activarAgregar = false;
        this.activarEliminar = false;
        this.activarEditar = false;
        this.listFunSeleccionados = [];
        this.route.params.forEach((params: Params) => {
            let id = +params['id'];
            if (id == 0) {
                this.newItem()
            } else {
                this.loadItem(id)
            }
        });
    }

    /**
     * @desc Función que crea una nueva instancia del objeto
     * punto de emision para crearlo por primera vez
     */
    newItem() {
        this.punto_emision = new PuntoEmision()
    }

    /**
     * @desc Función que recupera los datos asociados a
     * al punto de emisión e inicializa variables.
     * @param {Number} id
     */
    loadItem(id) {
        this.puntoEmisionServicio.getPuntoEmision(window.localStorage.getItem('auth_key'), id)
            .subscribe(resp => {
                    if (resp.status == 200) {
                        this.punto_emision = <PuntoEmision>resp.data.punto_emision;
                        this.punto_emision_uaa = <PuntoEmisionUAA[]>resp.data.punto_emision_uaa;
                    }
                }
            )
    }

    /**
     * @desc Función que guarda o actualiza los
     * datos asociados al punto de emisión
     */
    guardar() {
        this.puntoEmisionServicio.guardarPuntoEmision(window.localStorage.getItem('auth_key'), this.punto_emision)
            .subscribe(resp => {
                if (resp.status == 200) {
                    this.dialogService.notificacion('ÉXITO!', 'El Punto de Emisión ha sido guardado con éxito', this.viewContainerRef)
                        .subscribe(() => {
                            let link = ['home/recaudacion-punto-emision-detail', resp.data.id];
                            this.router.navigate(link)
                        });
                } else {
                    let msg = typeof (resp.message) == 'object' ? this.mensaje(resp.message) : resp.message;
                    this.dialogService.notificacion('ERROR!', msg, this.viewContainerRef)
                }
            })
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
     * @desc Función que almacena los items seleccionados para
     * proceder a ejecutar las operaciones definidas (delete)
     * @param {Punto de Emision UAA} item
     */
    selectedItem(item: PuntoEmision) {
        var idx = this.listFunSeleccionados.indexOf(item);
        if (idx > -1) {
            this.listFunSeleccionados.splice(idx, 1);
        } else {
            this.listFunSeleccionados.push(item);
        }
        this.changeBotones()
    }

    /**
     * @desc Función que actualiza el estado de las variables para habilitar
     * los botones del panel punto de emisión UAA
     */
    changeBotones() {
        if (this.listFunSeleccionados.length == 0) {
            this.activarEliminar = false;
            this.activarEditar = false;
        } else if (this.listFunSeleccionados.length == 1) {
            this.activarEliminar = true;
            this.activarEditar = true;
        } else {
            this.activarEliminar = true;
            this.activarEditar = false;
        }
    }

    /**
     * @desc Funcion que agrega el funcionario al
     * punto de emision actual
     */
    guardarFuncionario() {
        this.puntoEmisionServicio.guardarFuncionarioPuntoEmision(window.localStorage.getItem('auth_key'), this.punto_emision_uaa_new)
            .subscribe(resp => {
                if (resp.status == 200) {
                    this.dialogService.notificacion('ÉXITO!', 'El Funcionario ha sido guardado con éxito al Punto de Emisión', this.viewContainerRef)
                        .subscribe(() => {
                            this.ngOnInit()
                        });
                } else {
                    let msg = typeof (resp.message) == 'object' ? this.mensaje(resp.message) : resp.message;
                    this.dialogService.notificacion('ERROR!', msg, this.viewContainerRef)
                }
            })
    }

    /**
     * @desc Función que actualiza el estado de la variable que habilita
     * la opcion de agregar-editar Funcionarios al punto de Emision
     */
    mostrarFormularioFuncionario(opcion) {

        this.homeComponent.cambioEstadoCargando();
        this.funcionarioService.getFuncionariosPersona(window.localStorage.getItem('auth_key')).subscribe(resp => {
            this.listFun = resp.data;
            if (opcion == 1) {
                this.punto_emision_uaa_new = new PuntoEmisionUAA();
                this.punto_emision_uaa_new.impresora = "default";
            } else {
                this.punto_emision_uaa_new = Object.assign({}, this.listFunSeleccionados[0]);
                this.punto_emision_uaa_new.funcionario = this.punto_emision_uaa_new.funcionario['id'];
            }
            this.punto_emision_uaa_new.punto_emision = this.punto_emision.id;
            this.formPuntoEmisionUaa = this.formBuilder.group({
                'codigo': [this.punto_emision_uaa_new.codigo, [Validators.required, Validators.pattern('^[0-9]{3}$')]],
                'descripcion': [this.punto_emision_uaa_new.descripcion, Validators.required],
                'secuencial': [this.punto_emision_uaa_new.secuencial, [Validators.required, ValidacionService.validadorEsNumero]],
                'funcionario': [this.punto_emision_uaa_new.funcionario, Validators.required],
                'impresora': [this.punto_emision_uaa_new.impresora, Validators.required]
            });
            this.activarAgregar = true;
            this.homeComponent.cambioEstadoCargando();
        });
    }


    /**
     * @desc Función para confirmar si desea eliminar el Punto
     * de Emisión UAA (funcionario) del Punto de Emisión
     */
    confirmarEliminarFuncionario() {
        this.dialogService.confirm('Funcionario(s)', '¿Seguro desea eliminar los Funcionario(s) seleccionado(s) del Punto de Emisión?', this.viewContainerRef)
            .subscribe(res => {
                if (res == true) {
                    this.eliminarFuncionario()
                }
            });
    }

    /**
     * @desc Funcion que elimina un funcionario del
     * punto de emision
     */
    eliminarFuncionario() {
        let deleteExit = 0
        let deleteError = 0
        let msg = ""
        for (let i in this.listFunSeleccionados) {
            this.puntoEmisionServicio.deleteFuncionarioPuntoEmision(window.localStorage.getItem('auth_key'), this.listFunSeleccionados[i].id)
                .subscribe(res => {
                    res.status == 200 ? deleteExit += 1 : deleteError += 1
                    msg += res.message + '\n'
                    if ((deleteExit + deleteError) == this.listFunSeleccionados.length) {
                        this.dialogService.notificacion('ELIMINACIÓN DE FUNCIONARIO(S) - PUNTO DE EMISIÓN', msg, this.viewContainerRef)
                            .subscribe(() => {
                                this.ngOnInit()
                            });
                    }
                })
        }
    }

    /**
     * @desc Función que navega al componente que lo invoca,
     * el cual es listar puntos de emisión
     */
    regresar() {
        this.router.navigate(['home/recaudacion-punto-emision-list'])
    }
}
