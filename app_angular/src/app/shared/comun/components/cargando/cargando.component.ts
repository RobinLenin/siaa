import {Input, Component} from "@angular/core";

@Component({
    moduleId: module.id,
    selector: 'cargando',
    templateUrl: 'cargando.component.html'
})

export class CargandoComponent {

    @Input() titulo: string='Cargando...';
    @Input() color: string = 'warn';
    @Input() modo: string = 'indeterminate';
    @Input() progreso = 50;
    @Input() mostrar = 'progress-bar';

    constructor() {}


}