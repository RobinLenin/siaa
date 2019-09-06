import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {BuscarPipe} from "./buscar.pipe";
import {ResourceService} from "../../services/resource.service";

@NgModule(
    {
        imports: [
            FormsModule,
            CommonModule
        ],
        declarations: [
            BuscarPipe,
        ],
        providers:[
            ResourceService
        ],
        exports: [
            BuscarPipe
        ]
    }
)
export class BuscarPipeModule {
}