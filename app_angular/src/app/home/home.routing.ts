import {ModuleWithProviders} from "@angular/core";
import {Routes, RouterModule} from "@angular/router";
import {HomeComponent} from "./home.component";

const homeRoutes: Routes = [
    {
        path: 'home',
        component: HomeComponent,
        children: [
            {
                path: '',
                loadChildren: 'src/app/dashboard/dashboard.module#DashboardModule',
            },
            {
                path: '',
                loadChildren: 'src/app/recaudacion/recaudacion.module#RecaudacionModule'
            },
            {
                path: '',
                loadChildren: 'src/app/bienes/bien.module#BienModule'
            }
        ]
    }
];

export const HomeRouting: ModuleWithProviders = RouterModule.forChild(homeRoutes);
