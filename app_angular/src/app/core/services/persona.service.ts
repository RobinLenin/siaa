import {Injectable} from "@angular/core";
import { HttpClient} from "@angular/common/http";
import {Observable} from "rxjs/Observable";
import {PersonaResponse} from "../models/persona.model";
import {appService} from "../../credentials";
import {ResourceService} from "../../shared/comun/services/resource.service";
import "rxjs/add/operator/map";
import {DireccionesResponse} from "../models/direccion.model";

@Injectable()
export class PersonaService {

    constructor(private http: HttpClient,
                 private resourceService:ResourceService) {
    }

    /**
     * @desc Consume el API que obtiene la persona si existe en el siaaf, caso contrario consulta del
     * registro civil segun el número de identificación
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {String} numero_documento
     * @returns {Observable<TResult>}
     */
    getPersonaOrRegistrocivil(token: string, numero_documento: string) {
        let parametros = {numero_documento: numero_documento};
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<PersonaResponse>(appService.ws_core_persona_o_registrocivil, options)
    }

    /**
     * @desc Consume el API que obtiene la lista de direcciones de una persona
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} persona_id
     * @returns {Observable<TResult>}
     */
    getDireccionesPorPersona(token: string, persona_id: number) {
        let parametros = {persona_id: persona_id.toString()};
        let options = this.resourceService.getRequestOptions(token, parametros);
        return this.http.get<DireccionesResponse>(appService.ws_core_persona_lista_direcciones, options)
    }


}
