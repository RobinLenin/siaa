import {ModuleWithProviders} from "@angular/core";
import {Routes, RouterModule} from "@angular/router";
import {LoginComponent} from "./login.component";

const LoginRoutes: Routes = [
    {path: 'login', component: LoginComponent},
];

export const LoginRouting: ModuleWithProviders = RouterModule.forChild(LoginRoutes);
