import {NgModule} from "@angular/core";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {CommonModule} from "@angular/common";
import {FlexLayoutModule} from "@angular/flex-layout";
import {ToolbarAccionesModule} from "../shared/comun/components/toolbar-acciones/toolbar-acciones.module";
import {BuscarPersonaModule} from "../shared/core/components/buscar-persona/buscar-persona.module";
import {CalendarioModule} from "../shared/comun/components/calendario/calendario.module";
import {DialogModule} from "../shared/comun/components/dialog/dialog.module";
import {FechaMinMaxModule} from "../shared/comun/components/calendario/fecha-min-max.module";
import {SelectCatalogoItemModule} from "../shared/core/components/select-catalogo-item/select-item.module";
import {ValidadorModule} from "./../shared/comun/components/validador/validador.module";
import {
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatDatepickerModule,
    MatGridListModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatProgressBarModule,
    MatRadioModule,
    MatSelectModule,
    MatSnackBarModule,
    MatTableModule,
    MatToolbarModule,
    MatTreeModule
} from "@angular/material";
import {PaginadorScrollModule} from "../shared/comun/components/paginador-scroll/paginador-scroll.module";
import {PaginadorBuscarModule} from "../shared/comun/components/paginador-buscar/paginador-buscar.module";
import {BuscarPipeModule} from "../shared/comun/pipes/buscar/buscar.pipe.module";

import {FuncionarioService} from "../talento-humano/services/funcionario.service";
import {OrdenPagoService} from "./services/orden-pago.service";
import {PersonaService} from "../core/services/persona.service";
import {ProductoService} from "./services/producto.service";
import {PuntoEmisionService} from "./services/punto-emision.service";
import {UtilService} from "../shared/comun/services/util.service";
import {UAAService} from "../organico/services/uaa.services";

import {FacturaEmisionListComponent} from "./components/factura-emision/factura-emision-list.component";
import {ModalPagoComponent} from "./components/orden-pago/modal-pago.component";
import {OrdenPagoDetailComponent} from "./components/orden-pago/orden-pago-detail.component";
import {OrdenPagoListComponent} from "./components/orden-pago/orden-pago-list.component";
import {OrdenPagoValidarListComponent} from "./components/orden-pago/orden-pago-validar-list.component";
import {OrdenPagoValidarDetailComponent} from "./components/orden-pago/orden-pago-validar-detail.component";
import {ProductoDetailComponent} from "./components/producto/producto-detail.component";
import {ProductoListComponent} from "./components/producto/producto-list.component";
import {PuntoEmisionDetailComponent} from "./components/punto-emision/punto-emision-detail.component";
import {PuntoEmisionListComponent} from "./components/punto-emision/punto-emision-list.component";
import {ReportesRecaudacionAdminComponent} from "./components/reportes/reportes-recaudacion-admin.component";
import {ReportesRecaudacionUaaComponent} from "./components/reportes/reportes-recaudacion-uaa.component";
import {RecaudacionRouting} from "./recaudacion.routing";



@NgModule(
    {
        imports: [
            CommonModule,
            FormsModule,
            ReactiveFormsModule,
            ToolbarAccionesModule,
            BuscarPersonaModule,
            CalendarioModule,
            DialogModule,
            FechaMinMaxModule,
            PaginadorBuscarModule,
            PaginadorScrollModule,
            SelectCatalogoItemModule,
            ValidadorModule,
            MatDatepickerModule,
            MatToolbarModule,
            MatTableModule,
            MatCardModule,
            MatGridListModule,
            MatListModule,
            MatIconModule,
            MatButtonModule,
            MatInputModule,
            MatSelectModule,
            MatChipsModule,
            MatCheckboxModule,
            MatSnackBarModule,
            MatAutocompleteModule,
            MatTreeModule,
            MatProgressBarModule,
            MatRadioModule,
            FlexLayoutModule,
            BuscarPipeModule,
            RecaudacionRouting
        ],
        providers: [
            FuncionarioService,
            OrdenPagoService,
            ProductoService,
            PuntoEmisionService,
            PersonaService,
            UtilService,
            UAAService
        ],
        declarations: [
            FacturaEmisionListComponent,
            ModalPagoComponent,
            OrdenPagoListComponent,
            OrdenPagoDetailComponent,
            OrdenPagoValidarListComponent,
            OrdenPagoValidarDetailComponent,
            ProductoListComponent,
            ProductoDetailComponent,
            PuntoEmisionListComponent,
            PuntoEmisionDetailComponent,
            ReportesRecaudacionUaaComponent,
            ReportesRecaudacionAdminComponent,
        ],
        entryComponents: [
            ModalPagoComponent
        ],
    }
)
export class RecaudacionModule {
}
