import { Component, Input, Output, EventEmitter} from '@angular/core';

@Component({
    moduleId: module.id,
    selector: 'toolbar-acciones',
    templateUrl: 'toolbar-acciones.component.html'
})
export class ToolbarAccionesComponent {

    @Input() titulo: string;
    @Input() botones: any= {};
    @Input() resultado: number=0;
    @Input() masAcciones: any=[];

    @Input() activarBuscador: boolean = false;
    @Input() activarEditar: boolean = false;
    @Input() activarEliminar: boolean = false;
    @Input() activarImprimir: boolean = false;
    @Input() activarImprimirBlob: boolean = false;

    @Input() dataPDF: any;
    @Input() tipoPDF: string;
    @Input() departamentoPDF: string;
    @Input() columnsPDF: any;
    @Input() funcionPDF: any;

    @Output() notificadorInit = new EventEmitter();
    @Output() notificadorCrear = new EventEmitter();
    @Output() notificadorEditar = new EventEmitter();
    @Output() notificadorEliminar = new EventEmitter();
    @Output() notificadorBuscador = new EventEmitter();
    @Output() notificadorImprimirBlob = new EventEmitter();
    @Output() notificadorRegresar = new EventEmitter();
    @Output() notificadorEjecutarAccion = new EventEmitter();

    constructor() {

    }
    init() {
        this.notificadorInit.emit();
    }

    crear() {
        this.notificadorCrear.emit();
    }

    editar() {
        this.notificadorEditar.emit();
    }

    eliminar() {
        this.notificadorEliminar.emit();
    }

    imprimir(){
        this.notificadorImprimirBlob.emit()
    }

    buscar(){
        this.notificadorBuscador.emit()
    }

    regresar(){
        this.notificadorRegresar.emit()
    }

    ejecutarAccion(accion){
        this.notificadorEjecutarAccion.emit(accion)
    }

}
