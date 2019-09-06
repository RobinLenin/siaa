import {Component} from "@angular/core";
import {Router} from "@angular/router";


@Component({
    selector: 'siaaf',
    templateUrl: './app.component.html',
    //directives: [LoginComponent]

})
export class AppComponent {

    constructor(private router: Router) {
        var token = window.localStorage.getItem('auth_key');
        if (token != null) {
            this.router.navigate(['home'])
        } else {
            this.router.navigate(['login'])
        }
    }

}