import {Component, OnInit, ViewContainerRef} from "@angular/core";
import {FormBuilder, Validators} from "@angular/forms";
import {ValidacionService} from "../shared/comun/services/validacion.service";
import {Router} from "@angular/router";
import {UsuarioService} from "../seguridad/services/usuario.service";
import {DialogService} from "../shared/comun/services/dialog.service";

@Component({
    moduleId: module.id,
    selector: 'login',
    templateUrl: './login.component.html',
})

export class LoginComponent implements OnInit {

    loginForm: any;
    localUser = {username: '', password: ''};

    constructor(private formBuilder: FormBuilder,
                private viewContainerRef: ViewContainerRef,
                private router: Router,
                private usuarioService: UsuarioService,
                private dialogService: DialogService) {
    }

    /**
     * @desc Función que inicializa el formulario
     * de autenticación
     */
    ngOnInit() {
        this.loginForm = this.formBuilder.group({
            'username': ['', [Validators.required, ValidacionService.validadorEmail]],
            'password': ['', Validators.required]
        });
    }

    /**
     * @desc Función que obtiene el token de acuerdo a las credenciales
     * proporcionadas
     */
    login() {
        this.localUser.username = this.loginForm.value.username;
        this.localUser.password = this.loginForm.value.password;
        this.usuarioService.getLogin(this.localUser).then((res) => {
            if (res) {
                this.router.navigate(['home'])
            }else{
                 this.dialogService.notificacion('ERROR!', 'No puede iniciar sesión con las credenciales proporcionadas.', this.viewContainerRef)
            }
        });
    }
}
