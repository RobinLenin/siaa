import {Component, Input, Output, EventEmitter, OnInit} from "@angular/core";
import {ResourceService} from "../../services/resource.service";
import {StatusRestEnum, ComunEnum} from "../../utils/enums";

@Component({
    moduleId: module.id,
    selector: 'paginador-navegacion',
    templateUrl: 'paginador-navegacion.component.html'
})

export class PaginadorNavegacionComponent implements OnInit {

    @Input() servicioUrl: string;
    @Input() itemsPorPagina: number = 0;

    public paginasTotal: number;
    private itemsTotal: number;

    @Input() etiquetaTotal: string = "Total de registros";
    @Input() mostrarTotal: boolean = false;
    @Input() datos: any[] = [];
    @Input() pagina: number = 1;
    @Input() filtro: string;
    @Output() notificadorDatos = new EventEmitter();
    @Output() notificadorPagina = new EventEmitter();

    constructor(public resource: ResourceService) {
    }

    ngOnInit() {
        this.getData()
    }

    /**
     * Permite consultar una lista de objetos de un servicio
     * ingresado como parametro.
     */
    getData(): void {
        this.resource.getObjectsPagination(
        this.servicioUrl,
        localStorage.getItem(ComunEnum.AUTH_KEY),
        this.pagina,
        this.itemsPorPagina,
        this.filtro)
        .subscribe(res => {
        if (res.status == StatusRestEnum.HTTP_200_OK) {
        this.datos = res.data;
        this.paginasTotal = this.resource.numberTotalPages;
        this.itemsTotal = this.resource.numberTotalItems;
        this.notificadorDatos.emit(this.datos);
        this.notificadorPagina.emit(this.pagina);
        if (res.data.length > 0) {
        this.resource.keys = Object.keys(res.data[0]);
    }
}
});
}

/**
     * Cambios que se hacen en las variables que recibe el componente
     * @param {any} changes
     */
ngOnChanges(changes) {
    if ('filtro' in changes) {
        this.pagina=1;
        this.paginasTotal = this.resource.numberTotalPages;
        this.itemsTotal = this.resource.numberTotalItems;
    }else if ('datos' in changes) {
        this.paginasTotal = this.resource.numberTotalPages;
        this.itemsTotal = this.resource.numberTotalItems;
    }
}

/**
     * Permite ir a la siguiente pagina de una lista de paginas de acuerdo
     * al tamaño de la lista de objetos de un servicio.
     * @param {any} event
     */
nextPage(event): void {
    if (this.pagina <= this.paginasTotal) {
        if (!this.isLastPage()) {
            this.pagina++;
        }
        this.getData();
    }
}

/**
     * Permite ir a pagina anterior de una lista de paginas de acuerdo al
     * tamaño de la lista de objetos de un servicio.
     * @param {any} event
     */
previousPage(event): void {
    if (this.pagina >= 1) {
        if (!this.isFirstPage()) {
            this.pagina--;
        }
        this.getData();
    }
}

/**
     * Devuelve la ultima pagina.
     * @returns {boolean}
     */
isLastPage(): boolean {
    return this.pagina === this.paginasTotal;
}

/**
     * Devuelve la primera página.
     * @returns {boolean}
     */
isFirstPage(): boolean {
    return this.pagina === 1;
}

/**
     * Este metodo permite cambiar de pagina al hacer click en un item del paginator
     * @param {any} event
     * @param {any} numberOfPage
     */
changePage(event, numberOfPage): void {
    if (numberOfPage >= 1 && numberOfPage <= this.paginasTotal) {
        this.pagina = numberOfPage;
        this.getData();
    }
}

/**
     * Permite actualizar el paginador cuando se digita el número de pagina.
     * @param {any} event
     */
changeKeyPage(event): void {
    if (this.pagina > this.paginasTotal) {
        this.pagina = this.paginasTotal;
    } else if (this.pagina < 1) {
    this.pagina = 1;
}
this.getData();
}
}
