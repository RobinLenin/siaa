import {Component, Input, Output, EventEmitter, OnInit} from "@angular/core";
import {ResourceService} from "../../services/resource.service";
import {StatusRestEnum, ComunEnum} from "../../utils/enums";

@Component({
    moduleId: module.id,
    selector: 'paginador-scroll',
    templateUrl: 'paginador-scroll.component.html'
})
export class PaginadorScrollComponent implements OnInit {

    @Input() servicioUrl: string;
    @Input() itemsPorPagina: number;
    @Input() pagina: number;
    @Input() filtro: string;
    @Input() datos: any[] = [];

    @Input() mostrarBoton: boolean = true;
    @Input() mostrarTotal: boolean = true;
    @Input() etiquetaBoton: string = 'Mostrar mas...';
    @Input() etiquetaTotal: string = 'Total de items';

    @Output() notificadorDatos = new EventEmitter();
    @Output() notificadorPagina = new EventEmitter();

    visualizadosTotal: number;
    itemsTotal: number;
    habilitarBoton: boolean;

    constructor(private resourceService: ResourceService) {
    }

    ngOnInit() {
        if (this.mostrarBoton) {
            this.obtenerDatos();
        }
    }

    clickBoton() {
        this.pagina++;
        this.obtenerDatos();
    }

    obtenerDatos() {
        this.resourceService.getObjectsPagination(
            this.servicioUrl, localStorage.getItem(ComunEnum.AUTH_KEY),
            this.pagina, this.itemsPorPagina, this.filtro)
            .subscribe(res => {
                if (res.status == StatusRestEnum.HTTP_200_OK) {
                    this.datos = this.pagina==1 ? res.data : this.datos.concat(res.data);
                    this.notificadorDatos.emit(this.datos);
                    this.notificadorPagina.emit(this.pagina);
                    this.actualizarVariables();
                }
            });
    }

    actualizarVariables() {
        this.visualizadosTotal = this.datos.length;
        this.itemsTotal = this.resourceService.numberTotalItems;
        this.habilitarBoton = this.pagina >= this.resourceService.numberTotalPages ? false : true;
    }

    ngOnChanges(changes) {
        if('filtro' in changes){
            this.pagina=1;
            this.actualizarVariables()
        }else if ('datos' in changes) {
            this.actualizarVariables();
        }
    }
}