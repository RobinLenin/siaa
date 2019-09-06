import {NgModule, enableProdMode} from "@angular/core";
import {BrowserModule} from "@angular/platform-browser";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {HomeModule} from "./home/home.module";
import {LoginModule} from "./login/login.module";
import {AppComponent} from "./app.component";
import {Routing} from "./app.routing";
import { HttpClientModule } from '@angular/common/http';


@NgModule({
    imports: [
        Routing,
        BrowserModule,
        BrowserAnimationsModule,
        HomeModule,
        LoginModule,
        HttpClientModule
    ],
    declarations: [AppComponent],
    bootstrap: [AppComponent]
})
export class AppModule {
}
