import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule, MatIconModule, MatButtonModule, MatMenuModule } from '@angular/material';
import { ToolbarAccionesComponent } from './toolbar-acciones.component';
import { PlantillaImprimirModule } from '../plantilla-imprimir/plantilla-imprimir.module';

@NgModule(
    {
        imports: [
            CommonModule,
            MatToolbarModule,
            MatIconModule,
            MatButtonModule,
			PlantillaImprimirModule,
            MatMenuModule
        ],
        declarations: [
            ToolbarAccionesComponent
        ],
        exports: [
            ToolbarAccionesComponent
        ]
    }
)
export class ToolbarAccionesModule { }
