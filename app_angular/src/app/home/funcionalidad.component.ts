import {Component, Input} from "@angular/core";
import {Router} from "@angular/router";

@Component({
    selector: 'funcionalidad',
    templateUrl: './funcionalidad.component.html',
})
export class FuncionalidadComponent {

    @Input() funcionalidad;
    panelOpenState = false;

    constructor(private router: Router) {
    }

    changeNavegacion(item) {
        let link = ['home/' + item.formulario];
        this.router.navigate(link);
    }
}
