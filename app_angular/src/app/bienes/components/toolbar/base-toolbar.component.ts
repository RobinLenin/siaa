/* Autor: Yazber Romero.
 * Fecha: 07/08/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        07/08/2016                   	    Implementación inicial.
 */
import {Component, OnInit, EventEmitter, Output, Input} from "@angular/core";
import {Router, ActivatedRoute} from "@angular/router";
import {ResourceService} from "../../../shared/comun/services/resource.service";
import {FuncionalidadService} from "../../../seguridad/services/funcionalidad.service";
import {IAccionToolbar} from "./IAccionToolbar";
import {ComunEnum, DetalleParametrizacionEnum, AccionEnum} from "../../../shared/comun/utils/enums";
import { NotificationService } from '../../services/notificacion.service';
import { DetallePrestacionService } from '../../services/detalle-prestacion.service';

@Component({
    moduleId: module.id,
    selector: 'base-toolbar',
    templateUrl: 'base-toolbar.component.html'
})
export class BaseToolbarComponent implements OnInit {

    @Input() i_resultados: any[];
    @Input() titulo: string;
    @Input() url_nuevo: string;
    @Input() url_editar: string;
    @Input() url_retorno: string;
    @Input() url_actualizar: string;
    @Input() isVisible: boolean = true;
    @Input() isBuscador: boolean = false;
    @Input() i_numberOfItemsPerPage: number = 0;
    @Input() i_query: string;
    @Input() i_service: string;
    @Input() i_token: string;
    @Input() codToolbar: string;
    @Input() urlImprimir: string;
    @Input() dataImprimir: any;

    @Input() dataBruta: any;
    @Input() ejecutar: string;
    @Input() dataPDF: any;
    @Input() tipoPDF: string;
    @Input() departamentoPDF: string;
    @Input() columnsPDF: any;
    @Input() funcionPDF: any;

    @Input() i_multOperaciones: IAccionToolbar[] = [];
    @Input() i_pathGlobal: string[] = [];
    @Input() isNuevo = true;

    @Output() notificador = new EventEmitter();
    @Output() notificaGuardado = new EventEmitter();
    @Output() updateData = new EventEmitter();

    isEditar = false;
    isEliminar = false;
    operaciones = false;

    constructor(private detalleService: DetallePrestacionService,
                 private notificationService: NotificationService,
                 private router: Router, private resource: ResourceService,
                 private funcionalidadService: FuncionalidadService,
                 private route: ActivatedRoute) {
        let token = localStorage.getItem(ComunEnum.AUTH_KEY);
        this.i_token = token;
        this.i_numberOfItemsPerPage = Number(localStorage.getItem(DetalleParametrizacionEnum.ROWS_TABLE))
    }

    ngOnInit() {
        if (this.i_multOperaciones.length > 0) {
            this.operaciones = true;
        }

    }

    crear() {
        this.funcionalidadService.setCodigoFuncionalidad(AccionEnum.CREAR);
        let link = ['/' + this.url_nuevo];
        this.router.navigate(link);
    }

    editar() {
        this.funcionalidadService.setCodigoFuncionalidad(AccionEnum.EDITAR);
        let link = ['/' + this.url_editar];
        this.router.navigate(link);
    }

    retorno() {
        let link = ['/' + this.url_retorno];
        this.router.navigate(link);
    }

    guardar() {
        this.notificaGuardado.emit({ value: "3. llega a gurda a la base" });
    }

    limpiar() {
        this.notificationService.printWarningMessage("Modulo en construcción");
    }

    help() {
        this.notificationService.printWarningMessage("Modulo en construcción");
    }

    imprimir() {
        this.notificationService.printWarningMessage("Modulo en construcción");
    }

    eliminar() {
        this.notificationService.openConfirmationDialog("Esta por ACCION_ELIMINAR un Registro", ()=>{
            this.notificationService.printWarningMessage("Modulo en construcción");
        });
    }

    changeNavegacion(codigo, path) {
        this.funcionalidadService.setCodigoFuncionalidad(codigo);
        let link = ['/' + path];
        this.router.navigate(link);

    }

}
