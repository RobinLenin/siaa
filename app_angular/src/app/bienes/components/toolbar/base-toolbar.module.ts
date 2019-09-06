import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {MatToolbarModule, MatIconModule, MatButtonModule, MatMenuModule} from "@angular/material";
import {PaginadorBuscarModule} from "../../../shared/comun/components/paginador-buscar/paginador-buscar.module";
import {BaseToolbarComponent} from "./base-toolbar.component";
import { NotificationService } from '../../services/notificacion.service';
import {PlantillaImprimirModule} from "../../../shared/comun/components/plantilla-imprimir/plantilla-imprimir.module";

@NgModule({
	imports: [
		CommonModule,
		FormsModule,
		MatToolbarModule,
		MatIconModule,
		MatButtonModule,
		MatMenuModule,
		PaginadorBuscarModule,
		PlantillaImprimirModule
	],
	declarations: [BaseToolbarComponent,],
	providers:[NotificationService],
	exports: [BaseToolbarComponent]
})
export class BaseToolBarModule {
}
