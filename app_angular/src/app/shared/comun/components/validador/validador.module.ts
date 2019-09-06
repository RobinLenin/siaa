import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {ValidadorComponent} from "./validador.component";

@NgModule({
        imports: [
            CommonModule
        ],
        declarations: [
            ValidadorComponent
        ],
        exports: [
            ValidadorComponent
        ]
})
export class ValidadorModule { }