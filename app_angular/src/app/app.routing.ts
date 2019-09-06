import {ModuleWithProviders} from "@angular/core";
import {Routes, RouterModule} from "@angular/router";
import {AppComponent} from "./app.component";

export const routes: Routes = [
    {path: '', component: AppComponent},

];

export const Routing: ModuleWithProviders = RouterModule.forRoot(routes);