import { NgModule } from '@angular/core';
import { CommonModule,  } from '@angular/common';
import {DialogModule} from "../dialog/dialog.module";
import { PlantillaImprimirComponent } from './plantilla-imprimir.component';
import {MatIconModule,
		MatButtonModule,
		MatCheckboxModule,
		MatTableModule,
		MatToolbarModule} from '@angular/material';

@NgModule({
	imports: [
		CommonModule,
        DialogModule,
		MatIconModule,
		MatCheckboxModule,
		MatButtonModule,
		MatTableModule,
		MatToolbarModule
	],
	declarations: [PlantillaImprimirComponent],
	exports: [PlantillaImprimirComponent]
})
export class PlantillaImprimirModule { }
