import {NgModule} from "@angular/core";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MatCardModule, MatButtonModule, MatInputModule, MatFormFieldModule} from "@angular/material";
import {ValidadorModule} from "./../shared/comun/components/validador/validador.module";
import {DialogModule} from "../shared/comun/components/dialog/dialog.module";
import {LoginComponent} from "./login.component";
import {UsuarioService} from "../seguridad/services/usuario.service";
import {LoginRouting} from "./login.routing";

@NgModule({
    imports: [
        LoginRouting,
        FormsModule,
        ReactiveFormsModule,
        MatCardModule,
        MatButtonModule,
        MatInputModule,
        MatFormFieldModule,
        ValidadorModule,
        DialogModule
    ],
    exports: [MatButtonModule, MatInputModule],
    declarations: [
        LoginComponent
    ],
    providers: [
        UsuarioService
    ],
})

export class LoginModule {
}
