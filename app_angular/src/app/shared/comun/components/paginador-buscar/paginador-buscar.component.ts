import {Component, Input, Output, EventEmitter} from "@angular/core";
import {ResourceService} from "./../../services/resource.service";
import {StatusRestEnum, ComunEnum} from "../../utils/enums";

@Component({
    moduleId: module.id,
    selector: 'paginador-buscar',
    templateUrl: 'paginador-buscar.component.html',
})

export class PaginadorBuscarComponent {

    private buscando: boolean;

    @Input() servicioUrl: string;
    @Input() itemsPorPagina: number;
    @Input() pagina: number = 1;
    @Input() filtro: string;
    @Input() myStyles: any = {};

    @Input() disabled: boolean = false;
    @Input() placeholder: string = 'Buscar...';

    @Output() notificadorDatos = new EventEmitter();
    @Output() notificadorFiltro = new EventEmitter();
    @Output() notificadorEnter = new EventEmitter();

    limpiar: boolean = false;

    constructor(private resourceService: ResourceService) {
    }

    ngOnInit(){
        this.buscando = false;
    }

    /**
     * Permite obtener la lista de objetos cuando el filtro cambia de
     * estado y emite los datos al componente que lo solicita
     * @param {any} event
     */
    buscar(event): void {
        //Cuando se presiona enter no busca ya que existe los eventos keyup y keydown
        if(!this.buscando && event.keyCode!=13){
            this.buscando = true;
            this.resourceService.getObjectsPagination(
                this.servicioUrl, localStorage.getItem(ComunEnum.AUTH_KEY),
                this.pagina, this.itemsPorPagina, this.filtro)
                .subscribe( (res:PaginadorResponse) => {
                //if (res.status == StatusRestEnum.HTTP_200_OK) {
                this.notificadorDatos.emit(res.data);
                this.notificadorFiltro.emit(this.filtro);
                this.limpiar = this.filtro != '' ? true : false;
                //}
                this.buscando = false;
            });
        }
    }

    /**
     * Limpia el filtro, actualiza la lista de objetos y emite el valor
     * del filtro al componente que lo solicita
     * @param {any} event
     */
    limpiarBusqueda(event) {
        this.pagina = 1;
        this.filtro = '';
        this.buscar(event);
    }

    /**
     * Notifica cuando se realizo un enter en el input y envia el texto de busqueda
     * @param {any} event
     */
    onEnter(text){
      this.notificadorEnter.emit(text);
    }
}

export interface PaginadorResponse {
    data: any;
}
