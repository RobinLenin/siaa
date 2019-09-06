import {NgModule} from "@angular/core";
import {PaginadorScrollComponent} from "./paginador-scroll.component";
import {MatButtonModule, MatToolbarModule} from "@angular/material";
import {CommonModule} from "@angular/common";
import {ResourceService} from "../../services/resource.service";

@NgModule({
    imports:[
        CommonModule,
        MatButtonModule,
        MatToolbarModule,
    ],
    providers:[
        ResourceService
    ],
    declarations:[
        PaginadorScrollComponent
    ],
    exports:[
        PaginadorScrollComponent
    ]
})
export class PaginadorScrollModule{

}