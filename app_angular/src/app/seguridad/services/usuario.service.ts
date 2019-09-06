import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {appService} from "../../credentials";
import {Usuario} from "../models/usuario.model"

@Injectable()
export class UsuarioService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Obtiene el token del usuario que esta
     * solicitando autorización para iniciar sesión
     * @param {Object} usercreds - Username y Password
     */
    getLogin(usercreds) {
        return new Promise((resolve) => {
            let credenciales = 'username=' + usercreds.username + '&password=' + usercreds.password;
            let headers = {'Content-Type': 'application/x-www-form-urlencoded'};
            let options = {headers: headers};
            this.http.post<TokenResponse>(appService.ws_seguridad_loguin, credenciales, options).subscribe((data) => {
                    if (data.token) {
                        window.localStorage.setItem('auth_key', data.token);
                        resolve(true);
                    }
                }, (err) => {
                    resolve(false);
                }
            );
        });
    }

    /**
     * @desc Obtiene segun el token enviado como parametro,
     * información del usuario logueado
     * @returns {Observable<TResult>}
     */
    getUsuarioLogueado(token) {
        let options = this.resourceService.getRequestOptions(token);
        return this.http.get<Usuario>(appService.ws_seguridad_usuario_logueado, options);
    }

}

export interface TokenResponse {
    token: string;
}
