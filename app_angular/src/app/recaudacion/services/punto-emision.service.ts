import {HttpClient} from "@angular/common/http";
import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";
import {appService} from "../../credentials";
import {ResourceService} from "../../shared/comun/services/resource.service";
import {PuntoEmision, PuntoEmisionResponse, PuntosEmisionResponse} from "../models/punto-emison.model";
import {PuntoEmisionUAA, PuntoEmisionUAAResponse, PuntosEmisionUAAResponse} from "../models/punto-emision-uaa.model";

@Injectable()
export class PuntoEmisionService {

    constructor(private http: HttpClient,
                private resourceService: ResourceService) {
    }

    /**
     * @desc Obtiene la lista de puntos de emision del API
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Object|Array}
     */
    getPuntosEmision(token: string) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<PuntosEmisionResponse>(appService.ws_recaudacion_puntos_emision, options)
    }

    /**
     * @desc Consume el API para obtener un punto de emision que ya existe
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} id - Identificador del item
     * @returns {Observable<TResult>}
     */
    getPuntoEmision(token: string, id: number) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<PuntoEmisionUAAResponse>(appService.ws_recaudacion_puntos_emision + '/' + id, options)
    }

    /**
     * @desc Consume el API para elimina un PuntoEmision
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @param {Number} id - Identificador del item
     * @returns {Observable<TResult>}
     */
    deletePuntoEmision(token: string, id: number) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.delete<PuntoEmisionResponse>(appService.ws_recaudacion_puntos_emision + '/' + id, options)
    }

    /**
     * @desc Consume el API para guardar o actualizar un punto de emision
     * @param {Number} token
     * @param {PuntoEmision} data
     * @returns {Observable<TResult>}
     */
    guardarPuntoEmision(token: string, data: PuntoEmision) {
        let body = JSON.stringify(data);
        let options = this.resourceService.getRequestOptions(token)
        if (!data.id) {
            return this.http.post<PuntoEmisionResponse>(appService.ws_recaudacion_puntos_emision, body, options)
        } else {
            return this.http.put<PuntoEmisionResponse>(appService.ws_recaudacion_puntos_emision + '/' + data.id, body, options)
        }
    }

    /**
     * @desc Consume el API para asignar o actualizar un Funcionario al Punto de Emision
     * @param {Number} token
     * @param {PuntoEmisionUAA} data
     * @returns {Observable<TResult>}
     */
    guardarFuncionarioPuntoEmision(token: string, data: PuntoEmisionUAA) {
        let body = JSON.stringify(data);
        let options = this.resourceService.getRequestOptions(token);
        let id = data.id ? data.id : 0;
        return this.http.post<PuntoEmisionResponse>(appService.ws_recaudacion_puntos_emision + "/" + id + "/guardar_funcionario_in_punto_emision", body, options)
    }

    /**
     * @desc Consume el API para eliminar el Funcionario asignado al Punto de Emision
     * @param {Number} token
     * @param {PuntoEmision} data
     * @returns {Observable<TResult>}
     */
    deleteFuncionarioPuntoEmision(token: string, id: number) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.delete<PuntoEmisionResponse>(appService.ws_recaudacion_puntos_emision + "/" + id + "/eliminar_funcionario_in_punto_emision", options)
    }

    /**
     * @desc Obtiene la lista de puntos de emision UAA al que pertenece el funcionario
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Object|Array}
     */
    getPuntosEmisionUaaInFuncionario(token: string) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<PuntosEmisionUAAResponse>(appService.ws_recaudacion_puntos_emision + '/get_puntos_emision_uaa_in_funcionario', options);
    }

    /**
     * @desc Obtiene la lista de puntos de emision al que pertenece el funcionario
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Object|Array}
     */
    getPuntosEmisionInFuncionario(token: string) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<PuntosEmisionResponse>(appService.ws_recaudacion_puntos_emision + '/get_puntos_emision_in_funcionario', options)
    }

    /**
     * @desc Obtiene la lista de puntos de emision en estado activo
     * @param {String} token - Cadena de caracteres para la autenticacion en el API
     * @returns {Object|Array}
     */
    getPuntosEmisionActivo(token: string) {
        let options = this.resourceService.getRequestOptions(token)
        return this.http.get<PuntosEmisionResponse>(appService.ws_recaudacion_puntos_emision + '/get_puntos_emision_activo', options)
    }

}
