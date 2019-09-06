import {NgModule} from "@angular/core";
import {MatProgressBarModule, MatProgressSpinnerModule, MatCardModule} from "@angular/material";
import {CargandoComponent} from "./cargando.component";
import {CommonModule} from "@angular/common";

@NgModule({
    imports: [
        CommonModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatCardModule
    ],
    declarations: [
        CargandoComponent
    ],
    exports: [
        CargandoComponent
    ],
    entryComponents:[
        CargandoComponent
    ]
})

export class CargandoModule {
}