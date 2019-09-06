import {HttpClient} from "@angular/common/http";
import {Injectable} from "@angular/core";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";
import {appService} from "../../credentials";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {FuncionariosResponse} from "../models/funcionario.model";

@Injectable()
export class FuncionarioService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * Devuelve lista de funcionarios con datos principales de la persona
     * @desc Obtiene la lista funcionarios
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Object|Array}
     */
    getFuncionariosPersona(token: string) {
        let options = this.resourceService.getRequestOptions(token);
        return this.http.get<FuncionariosResponse>(appService.ws_talento_humano_funcionario_lista , options)
    }
}
