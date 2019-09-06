import {MatIconModule, MatToolbarModule, MatButtonModule, MatInputModule} from "@angular/material";
import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {PaginadorNavegacionComponent} from "./paginador-navegacion.component";
//import {TranslateModule} from "@ngx-translate/core";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        MatToolbarModule,
        MatIconModule,
        MatButtonModule,
        MatInputModule
    ],
    declarations: [
        PaginadorNavegacionComponent
    ],
    exports: [
        PaginadorNavegacionComponent
    ]
})
export class PaginadorNavegacionModule {
}
