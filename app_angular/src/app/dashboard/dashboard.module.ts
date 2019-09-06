import {NgModule} from "@angular/core";
import {MatCardModule, MatIconModule, MatToolbarModule} from "@angular/material";
import {CommonModule} from "@angular/common";
import {DashboardComponent} from "./dashboard.component";
import {DashboardRouting} from "./dashboard.routing";

@NgModule(
    {
        imports: [
            DashboardRouting,
            CommonModule,
            MatCardModule,
            MatIconModule,
            MatToolbarModule
        ],
        declarations: [
            DashboardComponent
        ]
    }
)
export class DashboardModule {
}
