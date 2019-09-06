import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {MatButtonModule, MatCheckboxModule, MatIconModule, MatListModule} from "@angular/material";
import {FlexLayoutModule} from "@angular/flex-layout";
import {PaginadorNavegacionModule} from '../../../comun/components/paginador-navegacion/paginador-navegacion.module';
import {PaginadorBuscarModule} from "../../../comun/components/paginador-buscar/paginador-buscar.module";
import {UtilService} from "../../../comun/services/util.service";
import {BuscarPersonaComponent} from "./buscar-persona.component";

@NgModule({
    imports: [
        CommonModule,
        MatListModule,
        MatCheckboxModule,
        MatButtonModule,
        MatIconModule,
        FlexLayoutModule,
        PaginadorNavegacionModule,
        PaginadorBuscarModule
    ],
    providers: [UtilService],
    declarations: [BuscarPersonaComponent],
    exports: [BuscarPersonaComponent],
})

export class BuscarPersonaModule {
}

