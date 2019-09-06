import {NgModule} from "@angular/core";
import {
    MatSidenavModule,
    MatCardModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatToolbarModule,
    MatTooltipModule,
    MatMenuModule,
    MatExpansionModule
} from "@angular/material";
import {CommonModule} from "@angular/common";
import {FlexLayoutModule} from "@angular/flex-layout";
import {TranslateModule} from "@ngx-translate/core";
import {CargandoModule} from "../shared/comun/components/cargando/cargando.module";
import {DetalleParametrizacionService} from "../configuracion/services/detalle-parametrizacion.service";
import {UsuarioService} from "../seguridad/services/usuario.service";
import {FuncionalidadService} from "../seguridad/services/funcionalidad.service";
import {ResourceService} from "../shared/comun/services/resource.service";
import {HomeRouting} from "./home.routing";
import {HomeComponent} from "./home.component";
import {FuncionalidadComponent} from "./funcionalidad.component";

@NgModule(
    {
        imports: [
            HomeRouting,
            CommonModule,
            MatSidenavModule,
            MatCardModule,
            MatListModule,
            MatIconModule,
            MatButtonModule,
            MatToolbarModule,
            MatTooltipModule,
            MatMenuModule,
            MatExpansionModule,
            TranslateModule.forRoot(),
            FlexLayoutModule,
            CargandoModule
        ],
        declarations: [HomeComponent, FuncionalidadComponent],
        providers: [
            DetalleParametrizacionService,
            FuncionalidadService,
            ResourceService,
            UsuarioService,
        ],
        exports: [
            HomeComponent
        ]
    }
)
export class HomeModule {
}
