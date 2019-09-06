import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {MatIconModule, MatInputModule, MatButtonModule, MatToolbarModule} from "@angular/material";
import {PaginadorBuscarComponent} from "./paginador-buscar.component";

@NgModule(
    {
        imports: [
            MatIconModule,
            MatInputModule,
            MatButtonModule,
            FormsModule,
            CommonModule,
            MatToolbarModule
        ],
        declarations: [PaginadorBuscarComponent],
        exports: [PaginadorBuscarComponent]
    }
)

export class PaginadorBuscarModule { }
