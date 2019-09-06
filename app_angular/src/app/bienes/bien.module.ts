import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {PrestacionModule} from "./components/prestacion/prestacion.module";
import {ReporteBienModule} from "./components/reportes/reporte-bien.module";

@NgModule({
    imports: [
        CommonModule,
        PrestacionModule,
        ReporteBienModule
    ],
    providers: [
    ]
})
export class BienModule { }
