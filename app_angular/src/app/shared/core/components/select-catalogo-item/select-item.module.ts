import {NgModule} from '@angular/core';
import {CommonModule} from "@angular/common";
import {FormsModule} from '@angular/forms';
import {MatSelectModule} from '@angular/material';
import {CatalogoItemService} from '../../../../core/services/catalogo-item.service';
import {SelectCatalogoItemComponent} from './select-item.component';

@NgModule(
    {
        imports: [
            FormsModule,
            CommonModule,
            MatSelectModule
        ],
        declarations: [SelectCatalogoItemComponent],
        providers: [CatalogoItemService],
        exports: [SelectCatalogoItemComponent]

    }
)
export class SelectCatalogoItemModule {
}
