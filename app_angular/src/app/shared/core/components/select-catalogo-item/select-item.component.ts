/* Autor: Yazber Romero.
 * Fecha: 08/08/2016
 * ----------------------------Historial---------------------------
 * Autor                     	Fecha:                           	Descripcion  
 * Yazber Romero      	        22/07/2016                   	    Implementación inicial.
 */
import {Component, OnInit, Input, Output, EventEmitter} from "@angular/core";
import {CatalogoItemService} from "../../../../core/services/catalogo-item.service";
import {CatalogoItem} from "../../../../core/models/catalogo-item.model";

@Component({
    moduleId: module.id,
    selector: 'select-item',
    templateUrl: 'select-item.component.html',
    providers: [CatalogoItemService]

})
export class SelectCatalogoItemComponent implements OnInit {

    @Input() items: CatalogoItem[];
    @Input() selectedValue = undefined;
    @Input() codCatalogo: string;
    @Input() isDisabled: boolean = false;
    @Input() isRequired: boolean = false;
    @Input() placeholder: string = 'Seleccione una opción';
    @Output() notificador = new EventEmitter();

    constructor(private serviceItems: CatalogoItemService) {
    }

    ngOnInit() {
        this.loadItems();
    }

    loadItems() {
        var token = window.localStorage.getItem('auth_key')
        return this.serviceItems.getItemsPorCatalogo(this.codCatalogo, token)
            .subscribe(res => {
                if (res.status == 200) {
                    this.items = res.data;
                }
            });
    }

    selectItem(newValue) {
        this.notificador.emit(newValue);
    }

}
