Validador de formularios en FrontEnd
==

Para la validación de formularios del lado del cliente se expone el ejemplo del login:

1. **Configurar el componente**

    ```
    import { FormBuilder, Validators } from '@angular/forms';
    import { ValidacionService } from './../shared/comun/services/validador/validacion.service';
    ```
    ```
    fb: (FormBuilder) {
        this.loginForm = this.formBuilder.group({
            'username': ['', [Validators.required, ValidacionService.validadorEmail]],
            'password': ['', Validators.required]
        });
    }
    ```

2. **Configurar el model**

    ```
    import { FormsModule, ReactiveFormsModule } from '@angular/forms';
    ```

3. **Configurar el html**

    ```
    <form [formGroup]="loginForm" (ngSubmit)="login()">
        <md-card-header>
            <md-card-title>SISTEMA DE INFORMACION ACADEMICO ADMINISTRATIVO FINANCIERO</md-card-title>
        </md-card-header>
        <img md-card-image src="img/perfil/logo-inicio.png">
        <md-card-content>
            <div class="form-group">
                <input formControlName="username" type="text" class="form-control" placeholder="Ingresa tu usuario">
                <control-errores [control]="loginForm.controls.username"></control-errores>
            </div>
            <div class="form-group">
                <input formControlName="password" type="password" class="form-control" placeholder="Ingresa tu contraseña">
                <control-errores [control]="loginForm.controls.password"></control-errores>
            </div>
        </md-card-content>
        <md-card-actions align="end">
            <button md-raised-button color="primary" type="submit" [disabled]="!loginForm.valid">Ingresar</button>
            <button md-raised-button color="primary">Cancelar</button>
        </md-card-actions>
    </form>
    ```

4. **Personalizar la validación** (validacion.service.ts)

    Aquí se configura el el mensaje que se va a mostrar

    ```
    static getValidadorMensajeError(validatorName: string, validatorValue?: any) {
        let config = {
            'required': 'Este campo es requerido!',
            'emailInvalido': 'El email ingresado es incorrecto!'
        };

        return config[validatorName];
    }
    ```
    
    Aquí se indica la validación personalizada
    ```
    static validadorEmail(control) {
        if (control.value.match(/[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/)) {
            return null;
        } else {
            return { 'emailInvalido': true };
        }
    }
    ```    
